from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.logging import setup_logging
from src.settings.ai import AISettings
from src.settings.auth import AuthSettings
from src.settings.database import DatabaseSettings
from src.settings.emails import EmailSettings
from src.settings.logging import LoggingSettings
from src.settings.redis import RedisSettings
from src.settings.security import SecuritySettings
from src.settings.solutions import SolutionSettings
from src.settings.storage import StorageSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    ENV: str = Field(description="Окружение")
    APP: str = Field(default="app", description="Сервис")
    PLATFORM_NAME: str = Field(default="AI Review", description="Название платформы")

    db: DatabaseSettings = DatabaseSettings()  # type: ignore[call-arg]
    auth: AuthSettings = AuthSettings()  # type: ignore[call-arg]
    ai: AISettings = AISettings()  # type: ignore[call-arg]
    logging: LoggingSettings = LoggingSettings()  # type: ignore[call-arg]
    storage: StorageSettings = StorageSettings()  # type: ignore[call-arg]
    email: EmailSettings = EmailSettings()  # type: ignore[call-arg]
    redis: RedisSettings = RedisSettings()  # type: ignore[call-arg]
    security: SecuritySettings = SecuritySettings()  # type: ignore[call-arg]
    solutions: SolutionSettings = SolutionSettings()  # type: ignore[call-arg]


settings = Settings()  # type: ignore[call-arg]
setup_logging(
    level=settings.logging.LEVEL,
    log_format=settings.logging.FORMAT,
)
ROOT_DIR = Path(__file__).parent.parent.parent
