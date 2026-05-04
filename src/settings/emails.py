from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants.emails import EmailSenderTypeEnum


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    TYPE: EmailSenderTypeEnum = Field(
        default=EmailSenderTypeEnum.DISABLE,
        description="Тип отправщика писем: MAILEROO, SMTP или DISABLE",
    )

    MAILEROO_FROM: str | None = Field(default=None, description="Электронная почта отправителя для рассылок")
    MAILEROO_FROM_DISPLAY_NAME: str | None = Field(
        default=None, description="Отображаемое имя отправителя для рассылок"
    )
    MAILEROO_API_KEY: str | None = Field(default=None, description="API ключ для Maileroo")

    SMTP_HOST: str | None = Field(default=None, description="SMTP хост")
    SMTP_PORT: int | None = Field(default=None, description="SMTP порт")
    SMTP_USER: str | None = Field(default=None, description="SMTP пользователь")
    SMTP_PASSWORD: str | None = Field(default=None, description="SMTP пароль")
    SMTP_FROM_EMAIL: str | None = Field(default=None, description="Электронная почта отправителя")
    SMTP_USE_TLS: bool | None = Field(default=None, description="Использовать TLS для SMTP")

    @model_validator(mode="after")
    def check_invariants(self) -> Self:
        if self.TYPE == EmailSenderTypeEnum.MAILEROO:
            if not self.MAILEROO_API_KEY:
                raise ValueError("EMAIL_MAILEROO_API_KEY обязателен при EMAIL_TYPE=MAILEROO")
            if not self.MAILEROO_FROM_DISPLAY_NAME:
                raise ValueError("EMAIL_MAILEROO_FROM_DISPLAY_NAME обязателен при EMAIL_TYPE=MAILEROO")
            if not self.MAILEROO_FROM:
                raise ValueError("EMAIL_MAILEROO_FROM обязателен при EMAIL_TYPE=MAILEROO")
        elif self.TYPE == EmailSenderTypeEnum.SMTP:
            if not self.SMTP_HOST:
                raise ValueError("EMAIL_SMTP_HOST обязателен при EMAIL_TYPE=SMTP")
            if not self.SMTP_PORT:
                raise ValueError("EMAIL_SMTP_PORT обязателен при EMAIL_TYPE=SMTP")
            if not self.SMTP_USER:
                raise ValueError("EMAIL_SMTP_USER обязателен при EMAIL_TYPE=SMTP")
            if not self.SMTP_PASSWORD:
                raise ValueError("EMAIL_SMTP_PASSWORD обязателен при EMAIL_TYPE=SMTP")
            if not self.SMTP_FROM_EMAIL:
                raise ValueError("EMAIL_SMTP_FROM_EMAIL обязателен при EMAIL_TYPE=SMTP")
            if self.SMTP_USE_TLS is None:
                raise ValueError("EMAIL_SMTP_USE_TLS обязателен при EMAIL_TYPE=SMTP")
        return self
