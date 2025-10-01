from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from .config import Settings


def configure_logging(settings: Settings) -> None:
    level = _parse_log_level(settings.log_level)
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
    ]

    renderer: structlog.typing.Processor
    if settings.log_json:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def _parse_log_level(value: str | int) -> int:
    if isinstance(value, int):
        return value
    normalized = value.upper()
    if normalized.isdigit():
        return int(normalized)
    level = logging.getLevelName(normalized)
    if isinstance(level, int):
        return level
    raise ValueError(f"Unsupported log level: {value}")
