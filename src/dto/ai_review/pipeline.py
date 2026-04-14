import datetime

from src.constants.ai_pipeline import PipelineStepEnum, PipelineTaskStatusEnum
from src.constants.ai_review import SolutionStatusEnum
from src.dto.common import BaseDTO


class PipelineTaskDTO(BaseDTO):
    id: int
    solution_id: int
    step: PipelineStepEnum
    status: PipelineTaskStatusEnum
    error_text: str | None
    duration: float | None
    last_checked_at: datetime.datetime | None
    created_at: datetime.datetime


class PipelineTaskUpdateDTO(BaseDTO):
    status: PipelineTaskStatusEnum | None = None
    error_text: str | None = None
    duration: float | None = None


class PipelineTaskFiltersDTO(BaseDTO):
    solution_id: int | None = None


class PipelineInfoDTO(BaseDTO):
    solution_id: int
    solution_status: SolutionStatusEnum
    solution_steps: list[PipelineStepEnum]
    pipeline_tasks: list[PipelineTaskDTO]
