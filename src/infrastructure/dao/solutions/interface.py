from abc import ABC, abstractmethod

from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionFiltersDTO,
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
    async def get_list(self, filters: SolutionFiltersDTO | None) -> list[SolutionShortResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, solution_id: int) -> None:
        raise NotImplementedError
