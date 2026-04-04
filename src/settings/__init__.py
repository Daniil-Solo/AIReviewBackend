from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.logging import setup_logging
from src.settings.database import DatabaseSettings
from src.settings.jwt import JWTSettings
from src.settings.logging import LoggingSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    ENV: str = Field(description="Окружение: dev или prod")
    APP: str = Field("app", description="Название приложения")

    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
setup_logging(
    level=settings.logging.LEVEL,
    log_format=settings.logging.FORMAT,
)
