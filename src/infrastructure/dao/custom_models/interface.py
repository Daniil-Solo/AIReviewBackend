from abc import ABC, abstractmethod

from src.dto.custom_models import (
    CustomModelDTO,
    CustomModelFiltersDTO,
)
from src.dto.custom_models.custom_models import CustomModelCreateDTO, CustomModelUpdateDTO


class CustomModelsDAO(ABC):
    @abstractmethod
    async def create(self, data: CustomModelCreateDTO, created_by: int) -> CustomModelDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, model_id: int) -> CustomModelDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, filters: CustomModelFiltersDTO | None = None) -> list[CustomModelDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, model_id: int, data: CustomModelUpdateDTO) -> CustomModelDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model_id: int) -> None:
        raise NotImplementedError
