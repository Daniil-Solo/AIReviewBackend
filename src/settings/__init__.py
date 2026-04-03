from pydantic_settings import BaseSettings, SettingsConfigDict

from src.settings.database import DatabaseSettings
from src.settings.jwt import JWTSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()


settings = Settings()
