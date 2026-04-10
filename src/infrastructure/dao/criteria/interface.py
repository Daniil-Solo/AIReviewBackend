from abc import ABC, abstractmethod

from src.dto.criteria.criteria import (
    CriterionCreateDTO,
    CriterionFiltersDTO,
    CriterionResponseDTO,
    CriterionUpdateDTO,
)


class CriteriaDAO(ABC):
    @abstractmethod
    async def create(self, data: CriterionCreateDTO, created_by: int) -> CriterionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, criterion_id: int) -> CriterionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, filters: CriterionFiltersDTO, created_by: int) -> list[CriterionResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, criterion_id: int, data: CriterionUpdateDTO) -> CriterionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, criterion_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_available_tags(self, created_by: int) -> list[str]:
        raise NotImplementedError
