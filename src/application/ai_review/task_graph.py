from src.constants.ai_pipeline import TASK_DEPENDENCIES, PipelineStepEnum


def is_step_ready(step: PipelineStepEnum, completed_steps: list[PipelineStepEnum]) -> bool:
    completed_set = set(completed_steps)
    deps_set = set(TASK_DEPENDENCIES[step])
    return deps_set.issubset(completed_set)
