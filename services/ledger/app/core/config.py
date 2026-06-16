from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8002
    DEV_USER_ID: UUID = DEV_USER_ID
    LEDGER_DATABASE_URL: str = (
        "postgresql+asyncpg://spend_ledger:change_me_ledger@postgres-ledger:5432/ledger_db"
    )
    SQLALCHEMY_ECHO: bool = False
    PROFILE_REQUESTS: bool = False


settings = Settings()
