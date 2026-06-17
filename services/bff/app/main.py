from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import APIRouter, FastAPI, Request

from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import setup_logging
from app.core.middleware import AuthMiddleware, RequestIdMiddleware, RequestLogMiddleware
from app.routes.auth import router as auth_router
from app.routes.exports import router as exports_router
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
register_error_handlers(app)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AuthMiddleware)
app.include_router(api)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(expenses_router)
app.include_router(reports_router)
app.include_router(exports_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    client: httpx.AsyncClient = request.app.state.http_client
    dependencies = (
        ("auth", f"{settings.AUTH_SERVICE_URL}/ready"),
        ("ledger", f"{settings.LEDGER_SERVICE_URL}/ready"),
    )
    if settings.EXPORT_ENABLED:
        dependencies += (("export", f"{settings.EXPORT_SERVICE_URL}/ready"),)

    for name, url in dependencies:
        try:
            response = await client.get(url, timeout=5.0)
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(name) from exc
        if response.status_code != 200:
            raise ServiceUnavailableError(name)
    return {"status": "ok"}
