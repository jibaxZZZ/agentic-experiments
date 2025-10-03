from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QueryStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class QueryCreate(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    thread_id: str | None = Field(default=None, description="Optional conversation identifier")


class QueryResponse(BaseModel):
    id: str
    thread_id: str | None
    question: str
    status: QueryStatus
    response_text: str | None
    created_at: datetime
    updated_at: datetime
    latency_seconds: float | None


class QueryDetail(QueryResponse):
    raw_result: dict[str, Any] | None
    error_message: str | None


class QueryList(BaseModel):
    items: list[QueryResponse]
    count: int
