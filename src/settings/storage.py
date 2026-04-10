from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="S3_")

    ENDPOINT: str = Field(description="S3 endpoint URL")
    ACCESS_KEY: str = Field(description="S3 access key")
    SECRET_KEY: str = Field(description="S3 secret key")
    BUCKET: str = Field(description="S3 bucket for solutions")
    USE_SSL: bool = Field(description="Use SSL for S3 connection")
