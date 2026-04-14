from abc import ABC, abstractmethod

from src.constants.ai_pipeline import PipelineTaskStatusEnum
from src.dto.ai_review.pipeline import PipelineTaskDTO


class PipelineTasksDAO(ABC):
    @abstractmethod
    async def create_tasks(self, solution_id: int, steps: list[str]) -> list[PipelineTaskDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_pending_task(self) -> PipelineTaskDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_running(self, task_id: int) -> PipelineTaskDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_completed(self, task_id: int) -> PipelineTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def mark_completed_task(self, solution_id: int, step: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def mark_failed(self, task_id: int, error_text: str) -> PipelineTaskDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_completed_steps(self, solution_id: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def get_solution_tasks(self, solution_id: int) -> list[PipelineTaskDTO]:
        raise NotImplementedError

    @abstractmethod
    async def delete_solution_tasks(self, solution_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_task_status(self, task_id: int, status: PipelineTaskStatusEnum) -> None:
        raise NotImplementedError
