from __future__ import annotations

import json
from typing import Any

import typer

from .runner import AgentRunner

app = typer.Typer(help="Interact with the SQL agent LLM")


def _format_result(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return json.dumps(result, ensure_ascii=False, indent=2)
    final = messages[-1]
    content = getattr(final, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
        if chunks:
            return "\n".join(chunks)
    return json.dumps(result, ensure_ascii=False, indent=2)


@app.command()
def query(
    question: str,
    thread_id: str | None = typer.Option(
        None,
        "--thread-id",
        "-t",
        help="Optional thread identifier to continue a previous conversation.",
    ),
) -> None:
    runner = AgentRunner()
    result = runner.run_query_sync(question, thread_id=thread_id)
    typer.echo(_format_result(result))


if __name__ == "__main__":
    app()
