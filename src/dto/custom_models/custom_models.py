import datetime

from pydantic import Field

from src.constants.ai_pipeline import PipelineStepEnum
from src.dto.common import BaseDTO


class CustomModelRequestCreateDTO(BaseDTO):
    name: str = Field(min_length=1, max_length=255, description="Название кастомной модели")
    model: str = Field(min_length=1, max_length=255, description="Название модели")
    base_url: str = Field(min_length=1, max_length=500, description="OpenAI-совместимый endpoint")
    api_key: str = Field(min_length=1, description="API ключ")


class CustomModelCreateDTO(BaseDTO):
    name: str = Field(description="Название кастомной модели")
    model: str = Field(description="Название модели")
    base_url: str = Field(description="OpenAI-совместимый endpoint")
    encrypted_api_key: str = Field(description="Зашифрованный API-ключ")
    workspace_id: int = Field(description="ID пространства")


class CustomModelRequestUpdateDTO(BaseDTO):
    name: str = Field(min_length=1, max_length=255, description="Название кастомной модели")
    base_url: str = Field(min_length=1, max_length=500, description="OpenAI-совместимый endpoint")
    api_key: str = Field(min_length=1, description="API ключ")
    model: str = Field(min_length=1, max_length=255, description="Название модели")


class CustomModelUpdateDTO(BaseDTO):
    name: str = Field(description="Название кастомной модели")
    model: str = Field(description="Название модели")
    base_url: str = Field(description="OpenAI-совместимый endpoint")
    encrypted_api_key: str = Field(description="Зашифрованный API-ключ")


class CustomModelDTO(BaseDTO):
    id: int = Field(description="ID модели")
    workspace_id: int = Field(description="ID пространства")
    name: str = Field(description="Название модели")
    model: str = Field(description="Название модели")
    base_url: str = Field(description="OpenAI-совместимый endpoint")
    encrypted_api_key: str = Field(description="Зашифрованный API-ключ")
    created_by: int = Field(description="ID создателя")
    created_at: datetime.datetime = Field(description="Дата создания")


class CustomModelWithAPIKeyDTO(BaseDTO):
    id: int = Field(description="ID модели")
    workspace_id: int = Field(description="ID пространства")
    name: str
    model: str
    base_url: str
    api_key: str
    created_by: int
    created_at: datetime.datetime


class CustomModelFiltersDTO(BaseDTO):
    workspace_id: int | None = Field(None, description="Фильтр по workspace")


class TaskStepsModelRequestCreateDTO(BaseDTO):
    steps: dict[PipelineStepEnum, int | None] = Field(
        description="Словарь шагов и ID моделей. Ключи - названия шагов, значения - ID модели или null",
    )


class TaskStepsModelUpsertDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    steps: dict[PipelineStepEnum, int | None] = Field(
        description="Словарь шагов и ID моделей. Ключи - названия шагов, значения - ID модели или null",
    )


class TaskStepsModelDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    steps: dict[PipelineStepEnum, int | None] = Field(description="Словарь шагов и ID моделей")
    created_at: datetime.datetime = Field(description="Дата создания")


class TaskStepsModelUpdateDTO(BaseDTO):
    steps: dict[str, int | None] = Field(
        description="Словарь шагов и ID моделей. Ключи - названия шагов, значения - ID модели или null",
    )
