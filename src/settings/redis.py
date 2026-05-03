from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="allow")

    ENABLED: bool = Field(default=True, description="Флаг подключения к Redis")
    HOST: str | None = Field(default=None, description="Хост Redis")
    PORT: int | None = Field(default=None, description="Порт Redis")
    DB: int | None = Field(default=None, description="Номер базы данных Redis")
    PASSWORD: str | None = Field(default=None, description="Пароль базы данных Redis")

    @model_validator(mode="after")
    def validate_redis_params(self) -> "RedisSettings":
        if self.ENABLED:
            if not self.HOST:
                raise ValueError("REDIS_HOST обязателен при REDIS_ENABLED=True")
            if not self.PORT:
                raise ValueError("REDIS_PORT обязателен при REDIS_ENABLED=True")
            if self.DB is None:
                raise ValueError("REDIS_DB обязателен при REDIS_ENABLED=True")
        return self
