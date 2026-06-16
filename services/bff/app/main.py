from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware

api = APIRouter(prefix="/api/v1", tags=["health"])


@api.get("/health")
async def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "bff"}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.include_router(api)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
