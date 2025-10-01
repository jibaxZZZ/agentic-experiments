from __future__ import annotations

import threading

import structlog
from prometheus_client import start_http_server

from .config import Settings

logger = structlog.get_logger(__name__)

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
