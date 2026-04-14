from src.constants.ai_pipeline import PipelineStepEnum, TASK_DEPENDENCIES, ALL_STEPS


def get_all_dependencies(step: PipelineStepEnum) -> set[PipelineStepEnum]:
    deps = set()
    to_visit = [step]
    while to_visit:
        current = to_visit.pop()
        for dep in TASK_DEPENDENCIES[current]:
            deps.add(dep)
            to_visit.append(dep)
    return deps


def is_step_ready(step: PipelineStepEnum, completed_steps: list[PipelineStepEnum]) -> bool:
    completed_set = set(completed_steps)
    deps_set = set(TASK_DEPENDENCIES[step])
    return completed_set == deps_set


def get_ready_steps(completed_steps: list[PipelineStepEnum]) -> list[PipelineStepEnum]:
    completed_set = set(completed_steps)
    ready = []
    for step in ALL_STEPS:
        if is_step_ready(step, completed_steps) and step not in completed_set:
            ready.append(step)
    return ready
