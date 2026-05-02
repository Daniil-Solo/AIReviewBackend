from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageTypeEnum(str, Enum):
    S3 = "s3"
    FILE = "file"


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STORAGE_")

    TYPE: StorageTypeEnum = Field(description="Storage type: s3 or file")
    FILE_BASE_PATH: str | None = Field(default=None, description="Base path for file storage")
    S3_ENDPOINT: str = Field(description="S3 endpoint URL")
    S3_ACCESS_KEY: str = Field(description="S3 access key")
    S3_SECRET_KEY: str = Field(description="S3 secret key")
    S3_SOLUTIONS_BUCKET: str = Field(description="S3 bucket for solutions")
    S3_SOLUTION_ARTIFACTS_BUCKET: str = Field(description="S3 bucket for solution artifacts")
    S3_USE_SSL: bool = Field(description="Use SSL for S3 connection")
