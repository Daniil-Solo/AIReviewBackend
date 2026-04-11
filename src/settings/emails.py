from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    # General
    FROM: str = Field(description="Электронная почта отправителя для рассылок")
    FROM_DISPLAY_NAME: str = Field(description="Отображаемое имя отправителя для рассылок")

    # Maileroo
    MAILEROO_API_KEY: str = Field(description="API ключ для Maileroo")
