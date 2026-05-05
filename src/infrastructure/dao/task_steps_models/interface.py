from abc import ABC, abstractmethod

from src.dto.custom_models import TaskStepsModelDTO
from src.dto.custom_models.custom_models import TaskStepsModelUpsertDTO


class TaskStepsModelsDAO(ABC):
    @abstractmethod
    async def upsert(self, data: TaskStepsModelUpsertDTO) -> TaskStepsModelDTO:
        raise NotImplementedError

    @abstractmethod
    async def get(self, task_id: int) -> TaskStepsModelDTO:
        raise NotImplementedError

    @abstractmethod
    async def clear_model_references(self, workspace_id: int, model_id: int) -> None:
        raise NotImplementedError
