from abc import ABC, abstractmethod

from src.constants.ai_pipeline import PipelineStepEnum
from src.dto.ai_review.pipeline import PipelineTaskDTO, PipelineTaskFiltersDTO, PipelineTaskUpdateDTO


class PipelineTasksDAO(ABC):
    @abstractmethod
    async def create_many(self, solution_id: int, steps: list[PipelineStepEnum]) -> list[PipelineTaskDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_ready_pending(self) -> PipelineTaskDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def update_last_checked_at(self, task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task_id: int, data: PipelineTaskUpdateDTO) -> PipelineTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, filters: PipelineTaskFiltersDTO) -> list[PipelineTaskDTO]:
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self, solution_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_many_not_completed(self, solution_id: int) -> None:
        raise NotImplementedError
