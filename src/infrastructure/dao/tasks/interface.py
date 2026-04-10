from abc import ABC, abstractmethod

from src.dto.tasks.tasks import (
    TaskCreateDTO,
    TaskFiltersDTO,
    TaskResponseDTO,
    TaskUpdateDTO,
)


class TasksDAO(ABC):
    @abstractmethod
    async def create(self, data: TaskCreateDTO, created_by: int) -> TaskResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: int) -> TaskResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task_id: int, data: TaskUpdateDTO) -> TaskResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, filters: TaskFiltersDTO) -> list[TaskResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_public_by_id(self, task_id: int) -> TaskResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, task_id: int) -> None:
        raise NotImplementedError
