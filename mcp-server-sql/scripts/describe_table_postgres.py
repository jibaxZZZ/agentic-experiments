from __future__ import annotations

import asyncio
import os
from typing import Any

from mcp_server_sql.server import build_server


async def main() -> None:
    os.environ.setdefault("METRICS_PORT", "8002")
    if os.environ["METRICS_PORT"] == "8001":
        os.environ["METRICS_PORT"] = "8002"
    server = build_server()
    result = await server.call_tool(
        "describe_table",
        {
            "database": "postgres",
            "table": "_idf_technicien",
        },
    )

    if isinstance(result, tuple):
        maybe_meta = result[-1]
        if isinstance(maybe_meta, dict) and "result" in maybe_meta:
            columns = maybe_meta["result"]  # type: ignore[assignment]
        else:
            columns = []
    elif isinstance(result, list):
        columns = result
    else:
        columns = []

    if not columns:
        print("No columns returned for table _idf_technicien")
        return

    header = ("column_name", "data_type", "is_nullable", "column_default")
    title_row = dict(zip(header, header))
    widths = [
        max(len(str(row.get(key, ""))) for row in [title_row, *columns])
        for key in header
    ]
    print(" | ".join(title.ljust(width) for title, width in zip(header, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in columns:
        print(
            " | ".join(
                str(row.get(key, "")).ljust(width)
                for key, width in zip(header, widths)
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
