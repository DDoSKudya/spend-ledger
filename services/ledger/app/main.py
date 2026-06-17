from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.categories.router import router as categories_router
from app.core.config import settings
from app.core.database import create_engine, create_session_factory
from app.core.error_handlers import register_error_handlers
from app.core.logging import setup_logging
from app.core.middleware import (
    DbSessionMiddleware,
    PyInstrumentMiddleware,
    RequestIdMiddleware,
    SqlProfileMiddleware,
)
from app.core.sql_counter import attach_sql_counter
from app.expenses.router import router as expenses_router
from app.reports.router import router as reports_router
from app.tags.router import router as tags_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    engine = create_engine()
    if settings.PROFILE_REQUESTS:
        attach_sql_counter(engine.sync_engine)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)
app.add_middleware(PyInstrumentMiddleware)
app.add_middleware(SqlProfileMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(DbSessionMiddleware)

app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(expenses_router)
app.include_router(reports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    from sqlalchemy import text

    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok"}
