from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    ENCRYPTION_KEY: str = Field(
        description="Секретный ключ для шифрования данных",
    )
