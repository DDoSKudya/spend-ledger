from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    PORT: int = 8002
    LEDGER_DATABASE_URL: str = (
        "postgresql+asyncpg://spend_ledger:change_me_ledger@postgres-ledger:5432/ledger_db"
    )
    SQLALCHEMY_ECHO: bool = False
    PROFILE_REQUESTS: bool = False
    ENABLE_PYINSTRUMENT: bool = False


settings = Settings()
