from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.categories.router import router as categories_router
from app.core.config import settings
from app.core.database import create_engine, create_session_factory
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware, SqlProfileMiddleware
from app.core.sql_counter import attach_sql_counter
from app.expenses.router import router as expenses_router
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
app.add_middleware(SqlProfileMiddleware)
app.add_middleware(RequestIdMiddleware)


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(expenses_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
