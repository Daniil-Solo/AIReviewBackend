from enum import StrEnum


class CriterionStageEnum(StrEnum):
    PROJECT_DOC = "PROJECT_DOC"
    CODEBASE = "CODEBASE"
    MANUAL = "MANUAL"


class CriterionCheckStatusEnum(StrEnum):
    SUFFICIENT = "SUFFICIENT"
    NEEDS_CODE = "NEEDS_CODE"
    NEEDS_STUDENT = "NEEDS_STUDENT"
    NEEDS_MANUAL = "NEEDS_MANUAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SolutionFormatEnum(StrEnum):
    ZIP = "ZIP"
    GITHUB = "GITHUB"


class SolutionStatusEnum(StrEnum):
    CREATED = "CREATED"
    ERROR = "ERROR"
    AI_REVIEW = "AI_REVIEW"
    WAITING_EXAM = "WAITING_EXAM"
    EXAMINATION = "EXAMINATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    REVIEWED = "REVIEWED"
