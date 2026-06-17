from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware
from app.jobs.router import router as exports_router
from app.jobs.storage import JobStore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    app.state.job_store = JobStore(settings.REDIS_URL)
    yield
    app.state.job_store.close()


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)
app.add_middleware(RequestIdMiddleware)
app.include_router(exports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    if not request.app.state.job_store.ping():
        from app.core.exceptions import AppError

        raise AppError("Redis is unavailable", "service_unavailable", 503)
    return {"status": "ok"}
