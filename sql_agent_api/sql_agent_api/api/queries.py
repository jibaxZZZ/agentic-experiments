from __future__ import annotations

from functools import lru_cache
from time import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import BaseMessage
from sql_agent_llm.config import Settings as AgentSettings
from sql_agent_llm.runner import AgentRunner

from ..agent_env import apply_agent_environment
from ..config import get_settings
from ..database import get_session
from ..metrics import observe_request
from ..models import QueryStatus
from ..repository import count_queries, create_query, get_query, list_queries, update_query
from ..schemas import QueryCreate, QueryDetail, QueryList, QueryResponse

router = APIRouter(prefix="/queries", tags=["queries"])


@lru_cache(maxsize=1)
def _runner_factory() -> AgentRunner:
    settings = get_settings()
    agent_settings = AgentSettings(
        _env_file=None,
        OPENAI_API_KEY=settings.openai_api_key,
        OPENAI_MODEL=settings.openai_model,
        OPENAI_API_BASE=settings.openai_api_base,
        MCP_SERVER_URL=str(settings.mcp_server_url),
        MCP_SSE_PATH=settings.mcp_sse_path,
        LOG_LEVEL=settings.log_level,
        LOG_JSON=settings.log_json,
        METRICS_HOST=settings.metrics_host,
        METRICS_PORT=settings.metrics_port + 1,
        LANGSMITH_API_KEY=settings.langsmith_api_key,
        LANGSMITH_PROJECT=settings.langsmith_project,
        LANGSMITH_ENDPOINT=settings.langsmith_endpoint,
    )
    apply_agent_environment(agent_settings)
    return AgentRunner(settings=agent_settings)


async def get_agent_runner() -> AgentRunner:
    return _runner_factory()


@router.post("", response_model=QueryDetail, status_code=status.HTTP_201_CREATED)
async def create_query_endpoint(
    payload: QueryCreate,
    runner: AgentRunner = Depends(get_agent_runner),
    session: AsyncSession = Depends(get_session),
) -> QueryDetail:
    start = time()
    record = await create_query(session, payload.question, payload.thread_id)
    await session.commit()

    try:
        result = await runner.run_query(payload.question, thread_id=payload.thread_id)
        response_text = _extract_text(result)
        sanitized_result = _sanitize_result(result)
        thread_id = sanitized_result.get("config", {}).get("thread_id") if isinstance(sanitized_result, dict) else payload.thread_id
        updated = await update_query(
            session,
            record,
            status=QueryStatus.SUCCESS,
            response_text=response_text,
            raw_result=sanitized_result,
            latency_seconds=time() - start,
            thread_id=thread_id,
        )
        await session.commit()
        await session.refresh(updated)
        observe_request(start, status="success")
        return _to_detail(updated)
    except Exception as exc:  # noqa: BLE001
        await session.rollback()
        refreshed = await get_query(session, record.id)
        target = refreshed or record
        failed_record = await update_query(
            session,
            target,
            status=QueryStatus.FAILED,
            error_message=str(exc),
            latency_seconds=time() - start,
        )
        await session.commit()
        await session.refresh(failed_record)
        observe_request(start, status="error")
        raise HTTPException(status_code=500, detail="Agent execution failed") from exc


@router.get("/{query_id}", response_model=QueryDetail)
async def get_query_endpoint(query_id: str, session: AsyncSession = Depends(get_session)) -> QueryDetail:
    record = await get_query(session, query_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return _to_detail(record)


@router.get("", response_model=QueryList)
async def list_queries_endpoint(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> QueryList:
    records = await list_queries(session, limit=limit, offset=offset)
    total = await count_queries(session)
    return QueryList(
        items=[_to_response(record) for record in records],
        count=total,
    )


def _extract_text(result) -> str | None:
    if isinstance(result, dict):
        messages = result.get("messages") or []
        if messages:
            final = messages[-1]
            content = getattr(final, "content", None)
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "\n".join(
                    part.get("text", "") if isinstance(part, dict) else str(part) for part in content
                ).strip() or None
        return result.get("answer")
    return str(result) if result is not None else None


def _sanitize_result(result):
    if isinstance(result, dict):
        return {key: _sanitize_result(value) for key, value in result.items()}
    if isinstance(result, list):
        return [_sanitize_result(item) for item in result]
    if isinstance(result, BaseMessage):
        return result.model_dump()
    return result


def _to_response(record) -> QueryResponse:
    return QueryResponse(
        id=record.id,
        thread_id=record.thread_id,
        question=record.question,
        status=QueryStatus(record.status),
        response_text=record.response_text,
        created_at=record.created_at,
        updated_at=record.updated_at,
        latency_seconds=record.latency_seconds,
    )


def _to_detail(record) -> QueryDetail:
    base = _to_response(record)
    return QueryDetail(
        **base.model_dump(),
        raw_result=record.raw_result,
        error_message=record.error_message,
    )
