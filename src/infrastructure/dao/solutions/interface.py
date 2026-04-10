from abc import ABC, abstractmethod

from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionResponseDTO,
    SolutionShortResponseDTO,
    SolutionUpdateDTO,
)


class SolutionsDAO(ABC):
    @abstractmethod
    async def create(self, data: SolutionCreateDTO, created_by: int) -> SolutionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, solution_id: int) -> SolutionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def update(self, solution_id: int, data: SolutionUpdateDTO) -> SolutionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list_by_task(self, task_id: int) -> list[SolutionShortResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, solution_id: int) -> None:
        raise NotImplementedError
