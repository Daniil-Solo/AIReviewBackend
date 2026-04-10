import datetime

from pydantic import Field

from src.constants.ai_review import SolutionFormatEnum, SolutionStatusEnum
from src.dto.common import BaseDTO


class SolutionCreateRequestDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения (ZIP/GITHUB)")


class SolutionCreateDTO(SolutionCreateRequestDTO):
    link: str = Field(description="Ссылка на решение (для GITHUB)")


class SolutionUpdateDTO(BaseDTO):
    status: SolutionStatusEnum | None = Field(default=None, description="Статус решения")
    steps: dict[str, str] | None = Field(default=None, description="Шаги проверки")
    human_grade: int | None = Field(default=None, description="Оценка преподавателя")
    human_feedback: str | None = Field(default=None, description="Отзыв преподавателя")
    ai_feedback: str | None = Field(default=None, description="Отзыв от AI")


class SolutionResponseDTO(BaseDTO):
    id: int = Field(description="ID решения")
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения")
    link: str = Field(description="Ссылка на решение")
    status: SolutionStatusEnum = Field(description="Статус решения")
    steps: dict[str, str] = Field(description="Шаги проверки")
    human_grade: int | None = Field(description="Оценка преподавателя")
    human_feedback: str | None = Field(description="Отзыв преподавателя")
    ai_feedback: str | None = Field(description="Отзыв от AI")
    created_by: int = Field(description="ID создателя")
    created_at: datetime.datetime = Field(description="Дата создания")


class SolutionShortResponseDTO(BaseDTO):
    id: int = Field(description="ID решения")
    task_id: int = Field(description="ID задачи")
    format: SolutionFormatEnum = Field(description="Формат решения")
    link: str = Field(description="Ссылка на решение")
    status: SolutionStatusEnum = Field(description="Статус решения")
    human_grade: int | None = Field(description="Оценка преподавателя")
    human_feedback: str | None = Field(description="Отзыв преподавателя")
    ai_feedback: str | None = Field(description="Отзыв от AI")
    created_at: datetime.datetime = Field(description="Дата создания")
    created_by: int = Field(description="ID создателя")


class SolutionFiltersDTO(BaseDTO):
    task_id: int | None = Field(default=None, description="ID задачи для фильтрации")
