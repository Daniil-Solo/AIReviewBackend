from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    LEVEL: str = Field(default="INFO", description="Уровень логирования: DEBUG, INFO, WARNING, ERROR")
    FORMAT: str = Field(default="json", description="Формат логов: console (dev) или json (prod)")

    LOKI_URL: str = Field(description="URL Loki для отправки логов")
    LOKI_ENABLED: bool = Field(default=True, description="Включить отправку логов в Loki")
    LOKI_BATCH_SIZE: int = Field(default=50, ge=1, description="Количество записей в батче для отправки в Loki")
    LOKI_MAX_BUFFER_SIZE: int = Field(
        default=1000, ge=100, description="Максимальный размер буфера логов для Loki (backpressure)"
    )
    LOKI_FLUSH_INTERVAL: float = Field(
        default=5.0, ge=1.0, description="Интервал принудительной отправки логов в Loki (секунды)"
    )
