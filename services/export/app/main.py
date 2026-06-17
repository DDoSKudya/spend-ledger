from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
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
app.add_middleware(RequestIdMiddleware)


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


app.include_router(exports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
