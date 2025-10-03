from __future__ import annotations

import asyncio

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .api.queries import router as queries_router
from .config import Settings, get_settings
from .database import get_engine, get_session
from .logging_config import configure_logging
from .metrics import launch_metrics_server
from .models import Base

app = FastAPI(title="SQL Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    configure_logging(settings)
    launch_metrics_server(settings)
    engine = await get_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def healthcheck(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(queries_router)


@app.get("/")
async def root(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "service": "sql-agent-api",
        "model": settings.openai_model,
    }
