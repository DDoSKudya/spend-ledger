from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.categories.router import router as categories_router
from app.core.config import settings
from app.core.database import create_engine
from app.core.middleware import register_pyinstrument_middleware, register_sql_profile_middleware
from app.core.sql_counter import attach_sql_counter
from app.expenses.router import router as expenses_router
from app.reports.router import router as reports_router
from app.tags.router import router as tags_router
from spend_ledger_common.database import check_database_ready, create_session_factory
from spend_ledger_common.error_handlers import register_error_handlers
from spend_ledger_common.logging import setup_logging
from spend_ledger_common.middleware import (
    register_db_session_middleware,
    register_request_id_middleware,
)


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
register_db_session_middleware(app)
register_pyinstrument_middleware(app)
register_sql_profile_middleware(app)
register_request_id_middleware(app, service_name="ledger")

app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(expenses_router)
app.include_router(reports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    await check_database_ready(request.app.state.session_factory)
    return {"status": "ok"}
