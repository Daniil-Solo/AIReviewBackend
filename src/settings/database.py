from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str = Field(description="Хост базы данных")
    PORT: int = Field(description="Порт базы данных")
    USER: str = Field(description="Логин пользователя базы данных")
    PASSWORD: str = Field(description="Пароль пользователя базы данных")
    DB: str = Field(description="Название базы данных")
    SQL_ECHO: bool = Field(default=False, description="Отображать SQL-запросы для дебага")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
