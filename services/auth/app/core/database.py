from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from spend_ledger_common.database import create_async_db_engine

__all__ = ["create_engine"]


def create_engine() -> AsyncEngine:
    return create_async_db_engine(settings.AUTH_DATABASE_URL)
