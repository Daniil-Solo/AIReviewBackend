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
    VALIDATE_PROJECT_DOC = "validate_project_doc"
    GRADE_BY_PROJECT_DOC = "grade_by_project_doc"
    GRADE_BY_CODEBASE = "grade_by_codebase"


# шаг пайплайна: список шагов, от которых он зависит
TASK_DEPENDENCIES: dict[PipelineStepEnum, list[PipelineStepEnum]] = {
    PipelineStepEnum.PREPARE_PROJECT_TREE: [],
    PipelineStepEnum.PREPARE_PROJECT_CONTENT: [],
    PipelineStepEnum.CREATE_PROJECT_DOC: [
        PipelineStepEnum.PREPARE_PROJECT_TREE,
        PipelineStepEnum.PREPARE_PROJECT_CONTENT,
    ],
    PipelineStepEnum.GRADE_BY_PROJECT_DOC: [PipelineStepEnum.VALIDATE_PROJECT_DOC],
    PipelineStepEnum.GRADE_BY_CODEBASE: [PipelineStepEnum.GRADE_BY_PROJECT_DOC],
}


ALL_STEPS: list[PipelineStepEnum] = [PipelineStepEnum(item) for item in list(PipelineStepEnum)]

LLM_STEPS: list[PipelineStepEnum] = [
    PipelineStepEnum.CREATE_PROJECT_DOC,
    PipelineStepEnum.GRADE_BY_PROJECT_DOC,
    PipelineStepEnum.GRADE_BY_CODEBASE,
]
