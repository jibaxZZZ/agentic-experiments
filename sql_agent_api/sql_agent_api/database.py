from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import Settings, get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def get_engine(settings: Settings | None = None):
    global _engine, _session_factory
    if _engine is None:
        settings = settings or get_settings()
        _engine = create_async_engine(str(settings.database_url), echo=False, future=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _session_factory
    if _session_factory is None:
        await get_engine()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session
