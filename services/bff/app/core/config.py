from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

JWT_LENGTH_MIN = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8000
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    LEDGER_SERVICE_URL: str = "http://ledger-service:8002"
    EXPORT_SERVICE_URL: str = "http://export-api:8003"
    EXPORT_ENABLED: bool = True
    JWT_SECRET: str = "change_me_jwt_secret_min_32_chars_dev_only"
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "refresh_token"

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, value: str, info) -> str:
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "production" and len(value) < JWT_LENGTH_MIN:
            raise ValueError(
                f"JWT_SECRET must be at least {JWT_LENGTH_MIN} characters in production"
            )
        return value


settings = Settings()
