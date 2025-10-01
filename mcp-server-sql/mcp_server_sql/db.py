from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, Iterable, Mapping

import structlog
from prometheus_client import Counter, Histogram
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

logger = structlog.get_logger(__name__)

_QUERY_COUNTER = Counter(
    "mcp_sql_queries_total",
    "Total number of SQL queries executed via MCP",
    labelnames=("database", "status"),
)
_QUERY_LATENCY = Histogram(
    "mcp_sql_query_latency_seconds",
    "Latency of SQL queries executed via MCP",
    labelnames=("database",),
)


class DatabaseManager:
    def __init__(self, dsn_by_name: Mapping[str, str]):
        self._engines: Dict[str, AsyncEngine] = {
            name: create_async_engine(dsn, pool_pre_ping=True)
            for name, dsn in dsn_by_name.items()
        }

    @property
    def available_databases(self) -> Iterable[str]:
        return self._engines.keys()

    async def close(self) -> None:
        await asyncio.gather(*[engine.dispose() for engine in self._engines.values()])

    async def test_connections(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for name, engine in self._engines.items():
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                results[name] = True
            except SQLAlchemyError as exc:  # pragma: no cover - defensive
                logger.warning("database_connection_failed", database=name, error=str(exc))
                results[name] = False
        return results

    async def list_tables(self, database: str) -> list[dict[str, Any]]:
        query = text(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema NOT IN (:ignore1, :ignore2, :ignore3, :ignore4) "
            "ORDER BY table_schema, table_name"
        )
        ignore = self._ignored_schemas(database)
        return await self._fetch_all(database, query, ignore)

    async def describe_table(self, database: str, schema: str | None, table: str) -> list[dict[str, Any]]:
        if schema:
            qualified = f"{schema}.{table}"
        else:
            qualified = table
        query = text(
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = :table_name"
            + (" AND table_schema = :schema" if schema else "")
            + " ORDER BY ordinal_position"
        )
        params: dict[str, Any] = {"table_name": table}
        if schema:
            params["schema"] = schema
        return await self._fetch_all(database, query, params)

    async def execute_read_query(
        self,
        database: str,
        query_text: str,
        parameters: Mapping[str, Any] | None = None,
        limit: int | None = 100,
    ) -> dict[str, Any]:
        _ensure_safe_query(query_text)
        params = dict(parameters or {})
        engine = self._require_engine(database)
        histogram = _QUERY_LATENCY.labels(database=database)
        counter = _QUERY_COUNTER.labels(database=database, status="success")
        with histogram.time():
            try:
                async with engine.connect() as conn:
                    stream = await conn.stream(text(query_text), params)
                    rows: list[dict[str, Any]] = []
                    columns: list[str] | None = None
                    async for row in stream.mappings():
                        if columns is None:
                            columns = list(row.keys())
                        rows.append(dict(row))
                        if limit is not None and len(rows) >= limit:
                            break
                    await stream.close()
            except SQLAlchemyError as exc:
                _QUERY_COUNTER.labels(database=database, status="error").inc()
                logger.error("sql_query_failed", database=database, error=str(exc))
                raise
        counter.inc()
        return {"columns": columns or [], "rows": rows, "row_count": len(rows)}

    async def _fetch_all(
        self, database: str, query: Any, params: Mapping[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        engine = self._require_engine(database)
        async with engine.connect() as conn:
            result = await conn.execute(query, params or {})
            return [dict(row) for row in result.mappings().all()]

    def _require_engine(self, database: str) -> AsyncEngine:
        try:
            return self._engines[database]
        except KeyError as exc:
            raise ValueError(f"Unknown database '{database}'. Available: {list(self._engines)}") from exc

    def _ignored_schemas(self, database: str) -> Mapping[str, str]:
        if database == "mysql":
            return {
                "ignore1": "information_schema",
                "ignore2": "mysql",
                "ignore3": "performance_schema",
                "ignore4": "sys",
            }
        return {
            "ignore1": "information_schema",
            "ignore2": "pg_catalog",
            "ignore3": "pg_toast",
            "ignore4": "pg_temp_1",
        }


def _ensure_safe_query(query_text: str) -> None:
    stripped = query_text.lstrip()
    if not stripped:
        raise ValueError("Query cannot be empty")
    first_token = stripped.split()[0].upper()
    allowed = {"SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN"}
    if first_token not in allowed:
        raise ValueError(
            "Only read-only SQL statements are permitted (SELECT/WITH/SHOW/DESCRIBE/EXPLAIN)."
        )
