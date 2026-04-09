from enum import StrEnum


class CriterionStageEnum(StrEnum):
    PROJECT_DOC = "project_doc"
    CODEBASE = "codebase"
    AUTO = "auto"
    MANUAL = "manual"


class CriterionCheckStatusEnum(StrEnum):
    SUFFICIENT = "sufficient"
    NEEDS_CODE = "needs_code"
    NEEDS_STUDENT = "needs_student"
    NEEDS_MANUAL = "needs_manual"
    NOT_APPLICABLE = "not_applicable"


class SolutionFormatEnum(StrEnum):
    ZIP = "zip"
    GITHUB = "github"


class SolutionStatusEnum(StrEnum):
    CREATED = "created"
    ERROR = "error"
    AI_REVIEW = "ai_review"
    WAITING_EXAM = "waiting_exam"
    EXAMINATION = "examination"
    HUMAN_REVIEW = "human_review"
    REVIEWED = "reviewed"
