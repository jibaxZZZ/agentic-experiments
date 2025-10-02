from __future__ import annotations

import threading

import structlog
from prometheus_client import Counter, Histogram, start_http_server

from .config import Settings

logger = structlog.get_logger(__name__)

_AGENT_REQUESTS = Counter(
    "sql_agent_llm_requests_total",
    "Total number of agent executions",
)
_TOOL_CALLS = Counter(
    "sql_agent_llm_tool_calls_total",
    "Tool call count grouped by tool name",
    labelnames=("tool", "status"),
)
_TOOL_LATENCY = Histogram(
    "sql_agent_llm_tool_latency_seconds",
    "Latency of individual MCP tool calls",
    labelnames=("tool",),
)

_metrics_started = False
_metrics_lock = threading.Lock()


def launch_metrics_server(settings: Settings) -> None:
    global _metrics_started
    with _metrics_lock:
        if _metrics_started:
            return
        start_http_server(settings.metrics_port, addr=settings.metrics_host)
        _metrics_started = True
        logger.info(
            "metrics_server_started",
            host=settings.metrics_host,
            port=settings.metrics_port,
        )


def record_agent_request() -> None:
    _AGENT_REQUESTS.inc()


def observe_tool_call(tool_name: str, seconds: float, *, success: bool) -> None:
    _TOOL_LATENCY.labels(tool=tool_name).observe(seconds)
    _TOOL_CALLS.labels(tool=tool_name, status="success" if success else "error").inc()
