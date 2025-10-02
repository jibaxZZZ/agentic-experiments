from __future__ import annotations

import json
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any, AsyncIterator

import structlog
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp import types

from .config import Settings
from .metrics import observe_tool_call

logger = structlog.get_logger(__name__)


class MCPToolError(RuntimeError):
    """Raised when an MCP tool call fails."""


class MCPToolClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session: ClientSession | None = None
        self._transport_cm: Any | None = None

    async def __aenter__(self) -> "MCPToolClient":
        self._transport_cm = sse_client(self._settings.mcp_sse_url)
        read_stream, write_stream = await self._transport_cm.__aenter__()
        self._session = ClientSession(read_stream, write_stream)
        await self._session.__aenter__()
        await self._session.initialize()
        logger.info("mcp_client_connected", url=self._settings.mcp_sse_url)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        if self._session is not None:
            await self._session.__aexit__(exc_type, exc, tb)
            self._session = None
        if self._transport_cm is not None:
            await self._transport_cm.__aexit__(exc_type, exc, tb)
            self._transport_cm = None
        logger.info("mcp_client_disconnected")

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("MCP session is not initialized")
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session.list_tools()
        return list(result.tools)

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        start = perf_counter()
        success = False
        try:
            result = await self.session.call_tool(name, arguments or {})
            if result.isError:
                raise MCPToolError(f"Tool {name} reported error")
            parsed = _parse_tool_result(result)
            success = True
            return parsed
        finally:
            observe_tool_call(name, perf_counter() - start, success=success)


def _parse_tool_result(result: types.CallToolResult) -> Any:
    if result.structuredContent is not None:
        return result.structuredContent

    parsed_texts: list[Any] = []
    for content in result.content:
        if isinstance(content, types.TextContent):
            parsed_texts.append(_maybe_json(content.text))
        else:
            parsed_texts.append(content.model_dump())

    if len(parsed_texts) == 1:
        return parsed_texts[0]
    return parsed_texts


def _maybe_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


@asynccontextmanager
async def connect_mcp(settings: Settings) -> AsyncIterator[MCPToolClient]:
    client = MCPToolClient(settings)
    await client.__aenter__()
    try:
        yield client
    finally:
        await client.__aexit__(None, None, None)
