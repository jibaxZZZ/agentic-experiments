from __future__ import annotations

from typing import Sequence
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import QueryRecord, QueryStatus


async def create_query(session: AsyncSession, question: str, thread_id: str | None) -> QueryRecord:
    record = QueryRecord(
        id=str(uuid4()),
        question=question,
        thread_id=thread_id,
        status=QueryStatus.RUNNING.value,
    )
    session.add(record)
    await session.flush()
    return record


async def update_query(
    session: AsyncSession,
    record: QueryRecord,
    *,
    status: QueryStatus,
    response_text: str | None = None,
    raw_result: dict | None = None,
    error_message: str | None = None,
    latency_seconds: float | None = None,
    thread_id: str | None = None,
) -> QueryRecord:
    record.status = status.value
    record.response_text = response_text
    record.raw_result = raw_result
    record.error_message = error_message
    record.latency_seconds = latency_seconds
    if thread_id:
        record.thread_id = thread_id
    await session.flush()
    return record


async def get_query(session: AsyncSession, query_id: str) -> QueryRecord | None:
    return await session.get(QueryRecord, query_id)


async def list_queries(session: AsyncSession, limit: int = 20, offset: int = 0) -> Sequence[QueryRecord]:
    stmt = (
        select(QueryRecord)
        .order_by(QueryRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_queries(session: AsyncSession) -> int:
    stmt = select(func.count(QueryRecord.id))
    result = await session.execute(stmt)
    return int(result.scalar_one())
