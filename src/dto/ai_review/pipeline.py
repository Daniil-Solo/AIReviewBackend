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
    created_at: datetime.datetime
    updated_at: datetime.datetime


class PipelineInfoDTO(BaseDTO):
    solution_id: int
    solution_status: SolutionStatusEnum
    solution_steps: list[PipelineStepEnum]
    pipeline_tasks: list[PipelineTaskDTO]