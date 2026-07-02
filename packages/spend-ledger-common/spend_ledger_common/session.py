from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_session_ctx: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)


def get_session() -> AsyncSession:
    session = _session_ctx.get()
    if session is None:
        raise RuntimeError("Database session is not open. Wrap the operation in session_scope().")
    return session


@asynccontextmanager
async def session_scope(session_factory: async_sessionmaker[AsyncSession]):
    session = session_factory()
    token = _session_ctx.set(session)
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        if session.in_transaction():
            if session.is_active:
                await session.commit()
            else:
                await session.rollback()
    finally:
        await session.close()
        _session_ctx.reset(token)
