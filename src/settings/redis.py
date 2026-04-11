from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="allow")

    ENABLED: bool = Field(default=True, description="Флаг подключения к Redis")
    HOST: str = Field(description="Хост Redis")
    PORT: int = Field(description="Порт Redis")
    DB: int = Field(description="Номер базы данных Redis")
    PASSWORD: str = Field(description="Пароль базы данных Redis")
