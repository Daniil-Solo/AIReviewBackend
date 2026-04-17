from enum import StrEnum


class PipelineTaskStatusEnum(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStepEnum(StrEnum):
    PREPARE_PROJECT_TREE = "prepare_project_tree"
    PREPARE_PROJECT_CONTENT = "prepare_project_content"
    CREATE_PROJECT_DOC = "create_project_doc"
    GENERATE_CRITIC = "critic"
    RESOLVE_GAPS = "resolve_gaps"
    IMPROVE_DOC = "improve_doc"


# шаг пайплайна: список шагов, от которых он зависит
TASK_DEPENDENCIES: dict[PipelineStepEnum, list[PipelineStepEnum]] = {
    PipelineStepEnum.PREPARE_PROJECT_TREE: [],
    PipelineStepEnum.PREPARE_PROJECT_CONTENT: [],
    PipelineStepEnum.CREATE_PROJECT_DOC: [
        PipelineStepEnum.PREPARE_PROJECT_TREE,
        PipelineStepEnum.PREPARE_PROJECT_CONTENT,
    ],
    PipelineStepEnum.GENERATE_CRITIC: [PipelineStepEnum.CREATE_PROJECT_DOC],
    PipelineStepEnum.RESOLVE_GAPS: [PipelineStepEnum.GENERATE_CRITIC],
    PipelineStepEnum.IMPROVE_DOC: [
        PipelineStepEnum.CREATE_PROJECT_DOC,
        PipelineStepEnum.RESOLVE_GAPS,
    ],
}


ALL_STEPS: list[PipelineStepEnum] = [PipelineStepEnum(item) for item in list(PipelineStepEnum)]
