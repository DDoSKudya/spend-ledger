from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
