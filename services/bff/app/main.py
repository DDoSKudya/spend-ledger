from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import AuthMiddleware, RequestIdMiddleware, RequestLogMiddleware
from app.routes.auth import router as auth_router
from app.routes.ledger import categories_router, expenses_router, reports_router, tags_router

api = APIRouter(prefix="/api/v1", tags=["health"])


@api.get("/health")
async def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "bff"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(api)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(expenses_router)
app.include_router(reports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
