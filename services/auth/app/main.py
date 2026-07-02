from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.core.config import settings
from app.core.database import create_engine
from app.core.middleware import auth_needs_db_session
from app.users.router import router as users_router
from spend_ledger_common.database import check_database_ready, create_session_factory
from spend_ledger_common.error_handlers import register_error_handlers
from spend_ledger_common.logging import setup_logging
from spend_ledger_common.middleware import (
    register_db_session_middleware,
    register_request_id_middleware,
    register_request_log_middleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)
register_db_session_middleware(app, needs_session=auth_needs_db_session)
register_request_id_middleware(app, service_name="auth")
register_request_log_middleware(app)

app.include_router(users_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    await check_database_ready(request.app.state.session_factory)
    return {"status": "ok"}
