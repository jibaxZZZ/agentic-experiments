from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
from mcp.server.fastmcp import Context, FastMCP

from .config import Settings, get_settings
from .db import DatabaseManager
from .logging_config import configure_logging
from .metrics import launch_metrics_server

logger = structlog.get_logger(__name__)


async def _log_context_message(ctx: Context | None, message: str) -> None:
    if ctx is None:
        return
    try:
        await ctx.info(message)
    except Exception as exc:  # pragma: no cover - best effort logging only
        logger.debug("context_log_failed", error=str(exc), message=message)


def build_server(
    settings: Settings | None = None,
    *,
    host: str | None = None,
    port: int | None = None,
) -> FastMCP:
    settings = settings or get_settings()
    configure_logging(settings)
    launch_metrics_server(settings)

    available = settings.get_available_databases()
    if not available:
        logger.warning("no_databases_configured")
    db_manager = DatabaseManager(available)

    @asynccontextmanager
    async def lifespan(app: FastMCP):  # noqa: ARG001 - app reserved for future use
        try:
            health = await db_manager.test_connections()
            logger.info("database_health", health=health)
            yield {"db_manager": db_manager}
        finally:
            await db_manager.close()
            logger.info("database_connections_closed")

    instructions = (
        "Tools to explore SQL databases. Configure connection strings via environment"
        " variables."
    )

    server = FastMCP(
        name="mcp-server-sql",
        instructions=instructions,
        lifespan=lifespan,
        host=host or settings.mcp_host,
        port=port or settings.mcp_port,
    )

    _register_tools(server, db_manager)
    return server


def _register_tools(server: FastMCP, db_manager: DatabaseManager) -> None:
    @server.tool(name="list_databases", description="List configured database connections")
    async def list_databases() -> list[str]:
        return list(db_manager.available_databases)

    @server.tool(
        name="list_tables",
        description="List tables available in a configured database",
    )
    async def list_tables(
        database: str,
        schema_filter: str | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        tables = await db_manager.list_tables(database)
        if schema_filter:
            needle = schema_filter.lower()
            filtered = []
            for table in tables:
                schema_name = (table.get("table_schema") or "").lower()
                table_name = (table.get("table_name") or "").lower()
                qualified = f"{schema_name}.{table_name}" if schema_name else table_name
                if needle in qualified:
                    filtered.append(table)
        else:
            filtered = tables
        await _log_context_message(
            ctx,
            f"list_tables database={database} schema_filter={schema_filter} count={len(filtered)}",
        )
        return filtered

    @server.tool(
        name="describe_table",
        description="Describe table columns and metadata",
    )
    async def describe_table(
        database: str,
        table: str,
        schema: str | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        details = await db_manager.describe_table(database, schema, table)
        await _log_context_message(
            ctx,
            f"describe_table database={database} schema={schema} table={table} columns={len(details)}",
        )
        return details

    @server.tool(
        name="run_sql_query",
        description=(
            "Execute a read-only SQL query and return rows. Parameters may be passed as"
            " a mapping."
        ),
    )
    async def run_sql_query(
        database: str,
        query: str,
        parameters: Dict[str, Any] | None = None,
        limit: int | None = 100,
        ctx: Context | None = None,
    ) -> Dict[str, Any]:
        result = await db_manager.execute_read_query(database, query, parameters, limit=limit)
        await _log_context_message(
            ctx,
            f"run_sql_query database={database} row_count={result['row_count']} limit={limit}",
        )
        return result


def run_server(
    transport: str | None = None,
    *,
    host: str | None = None,
    port: int | None = None,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    server = build_server(settings=settings, host=host, port=port)
    server.run(transport or settings.mcp_transport)
