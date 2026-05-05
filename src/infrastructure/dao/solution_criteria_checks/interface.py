from abc import ABC, abstractmethod

from src.dto.solutions.solution_criteria_checks import (
    SolutionCriteriaCheckCreateDTO,
    SolutionCriteriaCheckFiltersDTO,
    SolutionCriteriaCheckResponseDTO,
)


class SolutionCriteriaChecksDAO(ABC):
    @abstractmethod
    async def get_list(self, filters: SolutionCriteriaCheckFiltersDTO) -> list[SolutionCriteriaCheckResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_latest_by_solution(self, solution_id: int) -> list[SolutionCriteriaCheckResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: SolutionCriteriaCheckCreateDTO) -> SolutionCriteriaCheckResponseDTO:
        raise NotImplementedError
