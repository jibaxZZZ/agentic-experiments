from __future__ import annotations

import asyncio
import os
from typing import Any

import structlog

from .agent.graph import AgentGraph
from .config import Settings, get_settings
from .logging_config import configure_logging
from .metrics import launch_metrics_server, record_agent_request
from .mcp_client import connect_mcp

logger = structlog.get_logger(__name__)


class AgentRunner:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        configure_logging(self._settings)
        launch_metrics_server(self._settings)
        _configure_langsmith(self._settings)

    async def run_query(self, question: str, *, thread_id: str | None = None) -> dict[str, Any]:
        record_agent_request()
        async with connect_mcp(self._settings) as client:
            agent = AgentGraph(self._settings, client)
            logger.info("agent_run_started", question=question)
            result = await agent.run(question, thread_id=thread_id)
            logger.info("agent_run_completed")
            return result

    def run_query_sync(self, question: str, *, thread_id: str | None = None) -> dict[str, Any]:
        return asyncio.run(self.run_query(question, thread_id=thread_id))


def _configure_langsmith(settings: Settings) -> None:
    if settings.langsmith_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault(
            "LANGCHAIN_ENDPOINT",
            settings.langsmith_endpoint or "https://api.smith.langchain.com",
        )
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
        if settings.langsmith_project:
            os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
