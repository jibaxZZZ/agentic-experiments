# MCP Server SQL

MCP server exposing database-aware tools so agentic systems can explore Postgres and MySQL
schemas. The server focuses on read-only access, structured logging, and metrics so it can be
embedded safely in larger orchestration flows.

## Project Layout

- `.venv/` – virtual environment managed with `uv`
- `pyproject.toml` – project metadata and dependencies
- `mcp_server_sql/` – Python package with configuration, database logic, metrics, and CLI entrypoint
- `.env.example` – template for runtime configuration

## Getting Started

1. Create the virtual environment (once):
   ```bash
   uv venv .venv
   ```
2. Install dependencies:
   ```bash
   . .venv/bin/activate
   uv sync
   ```
3. Copy the environment template and populate connection strings:
   ```bash
   cp .env.example .env
   # Edit DATABASE_URL_POSTGRES and/or DATABASE_URL_MYSQL
   ```
   - Use SQLAlchemy async URLs, e.g. `postgresql+asyncpg://user:pass@localhost:5432/dbname`
   - MySQL URLs should leverage `aiomysql`: `mysql+aiomysql://user:pass@localhost:3306/dbname`

## Running the Server

The CLI defaults to the transport configured via `MCP_SERVER_TRANSPORT` (stdio by default):

```bash
uv run python -m mcp_server_sql.cli --transport sse --host 0.0.0.0 --port 8080
```

Available transports: `stdio`, `sse`, `streamable-http`. The metrics endpoint starts automatically on
`METRICS_HOST:METRICS_PORT` (Prometheus exposition format).

Logging is structured JSON (configurable with `LOG_JSON=false`), and the server refuses state-changing
SQL. Only `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, or `EXPLAIN` statements are accepted.

## Exposed Tools

- `list_databases` – enumerate configured connections
- `list_tables` – browse information_schema tables for a database, with optional schema filter
- `describe_table` – inspect column metadata
- `run_sql_query` – execute streaming, read-only SQL with optional parameters and row limit

All tool invocations emit structured logs and update Prometheus counters/histograms for observability.

## Next Steps

- Add automated tests (pytest) once real databases or fixtures are wired in
- Extend toolset with NL-to-SQL helpers (LangChain, CrewAI, etc.) when the agent layer is ready
- Provide Dockerfile and Compose manifests for consistent deployment once requirements stabilise
