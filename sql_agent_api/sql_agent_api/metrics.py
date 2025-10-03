from __future__ import annotations

import threading
from time import time

import structlog
from prometheus_client import Counter, Histogram, start_http_server

from .config import Settings

logger = structlog.get_logger(__name__)

_REQUEST_COUNTER = Counter(
    "sql_agent_api_requests_total",
    "Number of query requests processed",
    labelnames=("status",),
)
_LATENCY = Histogram(
    "sql_agent_api_request_latency_seconds",
    "Latency of agent executions",
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


def observe_request(start_time: float, *, status: str) -> None:
    duration = time() - start_time
    _LATENCY.observe(duration)
    _REQUEST_COUNTER.labels(status=status).inc()
