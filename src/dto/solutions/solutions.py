import datetime
from typing import Any

from pydantic import Field, field_validator

from src.constants.ai_pipeline import PipelineStepEnum
from src.constants.ai_review import SolutionFormatEnum, SolutionStatusEnum
from src.dto.common import BaseDTO
from src.dto.users.user import ShortUserDTO


class SolutionCreateRequestDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения")
    github_repo_link: str | None = Field(description="Ссылка на GitHub-репозиторий")
    github_repo_branch: str | None = Field(description="Ветка GitHub-репозитория")


class SolutionCreateDTO(SolutionCreateRequestDTO):
    artifact_path: str = Field(description="Путь до артефакта решения")


class SolutionUpdateDTO(BaseDTO):
    status: SolutionStatusEnum | None = Field(default=None, description="Статус решения")
    steps: list[PipelineStepEnum] | None = Field(default=None, description="Шаги проверки")
    human_grade: int | None = Field(default=None, description="Оценка преподавателя")
    human_feedback: str | None = Field(default=None, description="Отзыв преподавателя")
    label: str | None = Field(default=None, description="Метка решения")


class SolutionResponseDTO(BaseDTO):
    id: int = Field(description="ID решения")
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения")
    github_repo_link: str | None = Field(description="Ссылка на GitHub-репозиторий")
    github_repo_branch: str | None = Field(description="Ветка GitHub-репозитория")
    artifact_path: str = Field(description="Путь до артефакта решения")
    status: SolutionStatusEnum = Field(description="Статус решения")
    steps: list[PipelineStepEnum] = Field(description="Шаги проверки")
    human_grade: int | None = Field(description="Оценка преподавателя")
    human_feedback: str | None = Field(description="Отзыв преподавателя")
    ai_feedback: str | None = Field(description="Отзыв от AI")
    label: str = Field(default="", description="Метка решения")
    created_by: int = Field(description="ID создателя")
    created_at: datetime.datetime = Field(description="Дата создания")

    @field_validator("steps", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v: Any) -> list[PipelineStepEnum]:
        if v == {}:
            return []
        return v


class SolutionShortResponseDTO(BaseDTO):
    id: int = Field(description="ID решения")
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения")
    github_repo_link: str | None = Field(description="Ссылка на GitHub-репозиторий")
    github_repo_branch: str | None = Field(description="Ветка GitHub-репозитория")
    status: SolutionStatusEnum = Field(description="Статус решения")
    steps: list[PipelineStepEnum] = Field(description="Шаги проверки")
    human_grade: int | None = Field(description="Оценка преподавателя")
    human_feedback: str | None = Field(description="Отзыв преподавателя")
    ai_feedback: str | None = Field(description="Отзыв от AI")
    label: str = Field(default="", description="Метка решения")
    created_at: datetime.datetime = Field(description="Дата создания")
    created_by: int = Field(description="ID создателя")
    author: ShortUserDTO | None = Field(default=None, description="Информация об авторе решения")

    @field_validator("steps", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v: Any) -> list[PipelineStepEnum]:
        if v == {}:
            return []
        return v


class SolutionFiltersRequestDTO(BaseDTO):
    task_id: int | None = Field(default=None, description="ID задачи для фильтрации")


class SolutionFinalReviewDTO(BaseDTO):
    human_grade: int = Field(description="Оценка преподавателя", ge=0, le=100)
    human_feedback: str = Field(description="Обратная связь")


class SolutionFiltersDTO(BaseDTO):
    created_by: int | None = Field(default=None, description="ID создателя для фильтрации")
    task_id: int | None = Field(default=None, description="ID задачи для фильтрации")


class SolutionLabelUpdateDTO(BaseDTO):
    label: str = Field(description="Метка решения", max_length=255)
