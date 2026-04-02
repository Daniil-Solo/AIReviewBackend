from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "autoreviewer"
    PASSWORD: str = "autoreviewer"
    DB: str = "autoreviewer"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    HOST: str = "0.0.0.0"
    PORT: int = 8000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db: DatabaseSettings = DatabaseSettings()
    app: AppSettings = AppSettings()


settings = Settings()
