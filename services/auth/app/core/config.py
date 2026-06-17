from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8001
    AUTH_DATABASE_URL: str = (
        "postgresql+asyncpg://spend_auth:change_me_auth@postgres-auth:5432/auth_db"
    )
    JWT_SECRET: str = "change_me_jwt_secret_min_32_chars_dev_only"
    JWT_ACCESS_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, value: str, info) -> str:
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "production" and len(value) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters in production")
        return value


settings = Settings()
