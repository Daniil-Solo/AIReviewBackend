from pydantic import Field

from src.dto.common import BaseDTO


class TaskCriteriaCreateDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    criterion_id: int = Field(description="ID критерия")
    weight: float = Field(ge=0.0, le=1.0, description="Вес критерия (0.0-1.0)")


class TaskCriteriaUpdateWeightDTO(BaseDTO):
    weight: float = Field(ge=0.0, le=1.0, description="Вес критерия (0.0-1.0)")


class TaskCriteriaResponseDTO(BaseDTO):
    id: int = Field(description="ID связки задачи и критерия")
    task_id: int = Field(description="ID задачи")
    criterion_id: int = Field(description="ID критерия")
    weight: float = Field(description="Вес критерия")
