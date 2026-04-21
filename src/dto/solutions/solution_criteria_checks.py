import datetime

from pydantic import Field

from src.constants.ai_review import CriterionCheckStatusEnum, CriterionStageEnum
from src.dto.common import BaseDTO


class SolutionCriteriaCheckCreateDTO(BaseDTO):
    task_criterion_id: int = Field(description="ID связки задачи и критерия")
    solution_id: int = Field(description="ID решения")
    comment: str = Field(default="", description="Комментарий")
    stage: CriterionStageEnum = Field(description="Этап проверки")
    status: CriterionCheckStatusEnum = Field(description="Статус проверки")
    is_passed: bool | None = Field(default=None, description="Пройдена ли проверка")


class SolutionCriteriaCheckFiltersDTO(BaseDTO):
    task_criterion_id: int | None = Field(default=None, description="ID связки задачи и критерия")
    solution_id: int | None = Field(default=None, description="ID решения")


class SolutionCriteriaCheckCreateRequestDTO(BaseDTO):
    task_criterion_id: int = Field(description="ID связки задачи и критерия")
    is_passed: bool = Field(description="Пройдена ли проверка")
    comment: str = Field(default="", description="Комментарий")


class SolutionCriteriaCheckResponseDTO(SolutionCriteriaCheckCreateDTO):
    id: int = Field(description="ID проверки критерия")
    created_at: datetime.datetime = Field(description="Дата создания")
