import enum


class WorkspaceMemberRoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
