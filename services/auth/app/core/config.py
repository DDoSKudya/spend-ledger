from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8001
    AUTH_DATABASE_URL: str = (
        "postgresql+asyncpg://spend_auth:change_me_auth@postgres-auth:5432/auth_db"
    )
    JWT_SECRET: str = "change_me"
    JWT_ACCESS_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7


settings = Settings()
