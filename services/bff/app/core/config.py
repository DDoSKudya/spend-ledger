from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8000
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    LEDGER_SERVICE_URL: str = "http://ledger-service:8002"
    EXPORT_SERVICE_URL: str = "http://export-api:8003"
    JWT_SECRET: str = "change_me"
    JWT_ACCESS_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "refresh_token"


settings = Settings()
