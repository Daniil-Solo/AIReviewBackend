from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageTypeEnum(StrEnum):
    S3 = "S3"
    FILE = "FILE"


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STORAGE_")

    TYPE: StorageTypeEnum = Field(description="Storage type: S3 or FILE")

    FILE_BASE_PATH: str | None = Field(default=None, description="Путь для хранения файлов")

    S3_ENDPOINT: str | None = Field(default=None, description="S3 endpoint URL")
    S3_ACCESS_KEY: str | None = Field(default=None, description="S3 access key")
    S3_SECRET_KEY: str | None = Field(default=None, description="S3 secret key")
    S3_SOLUTIONS_BUCKET: str | None = Field(default=None, description="S3 bucket for solutions")
    S3_SOLUTION_ARTIFACTS_BUCKET: str | None = Field(default=None, description="S3 bucket for solution artifacts")
    S3_USE_SSL: bool | None = Field(default=None, description="Use SSL for S3 connection")

    @model_validator(mode="after")
    def check_invariants(self) -> Self:
        if self.TYPE == StorageTypeEnum.FILE:
            if not self.FILE_BASE_PATH:
                raise ValueError("STORAGE_FILE_BASE_PATH обязателен при STORAGE_TYPE=FILE")
        elif self.TYPE == StorageTypeEnum.S3:
            if not self.S3_ENDPOINT:
                raise ValueError("STORAGE_S3_ENDPOINT обязателен при STORAGE_TYPE=S3")
            if not self.S3_ACCESS_KEY:
                raise ValueError("STORAGE_S3_ACCESS_KEY обязателен при STORAGE_TYPE=S3")
            if not self.S3_SECRET_KEY:
                raise ValueError("STORAGE_S3_SECRET_KEY обязателен при STORAGE_TYPE=S3")
            if not self.S3_SOLUTIONS_BUCKET:
                raise ValueError("STORAGE_S3_SOLUTIONS_BUCKET обязателен при STORAGE_TYPE=S3")
            if not self.S3_SOLUTION_ARTIFACTS_BUCKET:
                raise ValueError("STORAGE_S3_SOLUTION_ARTIFACTS_BUCKET обязателен при STORAGE_TYPE=S3")
            if self.S3_USE_SSL is None:
                raise ValueError("STORAGE_S3_USE_SSL обязателен при STORAGE_TYPE=S3")
        return self
