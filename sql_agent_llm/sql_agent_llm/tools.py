from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from .mcp_client import MCPToolClient


class ListDatabasesInput(BaseModel):
    """Input schema: no parameters."""


class ListTablesInput(BaseModel):
    database: str = Field(..., description="Logical database identifier (postgres or mysql)")
    schema_filter: str | None = Field(
        default=None,
        description="Optional case-insensitive filter applied to schema.table name",
    )


class DescribeTableInput(BaseModel):
    database: str = Field(..., description="Logical database identifier (postgres or mysql)")
    table: str = Field(..., description="Target table name")
    table_schema: str | None = Field(default=None, description="Optional schema name for the table")


class RunSqlQueryInput(BaseModel):
    database: str = Field(..., description="Logical database identifier (postgres or mysql)")
    query: str = Field(..., description="Read-only SQL query to execute")
    limit: int | None = Field(
        default=100,
        ge=1,
        description="Optional cap on returned rows",
    )


def build_tools(client: MCPToolClient) -> list[StructuredTool]:
    async def list_databases() -> str:
        result = await client.call_tool("list_databases")
        return json.dumps(result, ensure_ascii=False)

    async def list_tables(database: str, schema_filter: str | None = None) -> str:
        payload: dict[str, Any] = {"database": database}
        if schema_filter:
            payload["schema_filter"] = schema_filter
        result = await client.call_tool("list_tables", payload)
        return json.dumps(result, ensure_ascii=False)

    async def describe_table(database: str, table: str, table_schema: str | None = None) -> str:
        payload: dict[str, Any] = {"database": database, "table": table}
        if table_schema:
            payload["schema"] = table_schema
        result = await client.call_tool("describe_table", payload)
        return json.dumps(result, ensure_ascii=False)

    async def run_sql_query(database: str, query: str, limit: int | None = 100) -> str:
        payload: dict[str, Any] = {
            "database": database,
            "query": query,
            "limit": limit,
        }
        result = await client.call_tool("run_sql_query", payload)
        return json.dumps(result, ensure_ascii=False)

    return [
        StructuredTool.from_function(
            coroutine=list_databases,
            name="list_databases",
            description="Enumerate logical database connections exposed by the MCP server",
            args_schema=ListDatabasesInput,
        ),
        StructuredTool.from_function(
            coroutine=list_tables,
            name="list_tables",
            description=(
                "List tables and schemas within a database. Use schema_filter for narrower matches."
            ),
            args_schema=ListTablesInput,
        ),
        StructuredTool.from_function(
            coroutine=describe_table,
            name="describe_table",
            description="Retrieve column metadata for a given table (optionally schema-qualified).",
            args_schema=DescribeTableInput,
        ),
        StructuredTool.from_function(
            coroutine=run_sql_query,
            name="run_sql_query",
            description="Execute a read-only SQL query via the MCP server and receive rows as JSON.",
            args_schema=RunSqlQueryInput,
        ),
    ]
