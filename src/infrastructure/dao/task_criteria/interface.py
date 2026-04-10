from abc import ABC, abstractmethod

from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateDTO,
    TaskCriteriaResponseDTO,
    TaskCriteriaUpdateWeightDTO,
)


class TaskCriteriaDAO(ABC):
    @abstractmethod
    async def create(self, data: TaskCriteriaCreateDTO) -> TaskCriteriaResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_criterion_id: int) -> TaskCriteriaResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task_criterion_id: int, data: TaskCriteriaUpdateWeightDTO) -> TaskCriteriaResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, task_criterion_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_task_id(self, task_id: int) -> list[TaskCriteriaResponseDTO]:
        raise NotImplementedError
