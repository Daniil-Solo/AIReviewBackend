from pydantic import Field

from src.dto.common import BaseDTO
from src.dto.criteria import CriterionResponseDTO


class TaskCriteriaCreateRequestDTO(BaseDTO):
    criterion_id: int = Field(description="ID критерия")
    weight: float = Field(ge=0.0, description="Вес критерия")

class TaskCriteriaCreateBatchDTO(BaseDTO):
    criterion_ids: list[int] = Field(description="Список ID критериев")

class TaskCriteriaCreateDTO(TaskCriteriaCreateRequestDTO):
    task_id: int = Field(description="ID задачи")


class TaskCriteriaUpdateWeightDTO(BaseDTO):
    weight: float = Field(ge=0.0, description="Вес критерия")


class TaskCriteriaResponseDTO(BaseDTO):
    id: int = Field(description="ID связки задачи и критерия")
    task_id: int = Field(description="ID задачи")
    criterion_id: int = Field(description="ID критерия")
    weight: float = Field(description="Вес критерия")


class TaskCriteriaFullResponseDTO(TaskCriteriaResponseDTO):
    criterion: CriterionResponseDTO

