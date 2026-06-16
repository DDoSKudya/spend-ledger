from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8003
    REDIS_URL: str = "redis://redis:6379/0"
    EXPORT_FILES_DIR: str = "/data/exports"
    LEDGER_SERVICE_URL: str = "http://ledger-service:8002"


settings = Settings()
