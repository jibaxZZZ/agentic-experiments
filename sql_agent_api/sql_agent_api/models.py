from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QueryStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class QueryRecord(Base):
    __tablename__ = "query_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    thread_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    question: Mapped[str] = mapped_column(String(2000))
    status: Mapped[QueryStatus] = mapped_column(String(20), default=QueryStatus.PENDING.value)
    response_text: Mapped[str | None] = mapped_column(String(8000), nullable=True)
    raw_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    latency_seconds: Mapped[float | None] = mapped_column(nullable=True)
