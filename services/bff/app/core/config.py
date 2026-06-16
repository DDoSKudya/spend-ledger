from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8000
    DEV_USER_ID: UUID = DEV_USER_ID
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    LEDGER_SERVICE_URL: str = "http://ledger-service:8002"
    EXPORT_SERVICE_URL: str = "http://export-api:8003"
    JWT_SECRET: str = "change_me"


settings = Settings()
