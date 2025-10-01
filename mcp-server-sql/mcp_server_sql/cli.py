from __future__ import annotations

import typer

from .server import run_server

app = typer.Typer(help="Run the MCP SQL server")


@app.command()
def serve(
    transport: str | None = typer.Option(
        None,
        "--transport",
        "-t",
        help="Transport to run (stdio, sse, streamable-http). Defaults to env configuration.",
        case_sensitive=False,
    ),
    host: str | None = typer.Option(None, help="Host interface for SSE/HTTP transports"),
    port: int | None = typer.Option(None, help="Port for SSE/HTTP transports"),
) -> None:
    run_server(transport=transport, host=host, port=port)


if __name__ == "__main__":
    app()
