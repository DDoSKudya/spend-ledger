from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.core.config import settings
from app.jobs.router import router as exports_router
from app.jobs.storage import JobStore
from spend_ledger_common.error_handlers import register_error_handlers
from spend_ledger_common.exceptions import AppError
from spend_ledger_common.logging import setup_logging
from spend_ledger_common.middleware import (
    register_request_id_middleware,
    register_request_log_middleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    app.state.job_store = JobStore(settings.REDIS_URL)
    yield
    app.state.job_store.close()


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)
register_request_log_middleware(app)
register_request_id_middleware(app, service_name="export")
app.include_router(exports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    if not request.app.state.job_store.ping():
        raise AppError("Redis is unavailable", "service_unavailable", 503)
    return {"status": "ok"}
