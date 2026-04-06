import datetime

from pydantic import Field

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.common import BaseDTO


class WorkspaceJoinRuleBaseCreateDTO(BaseDTO):
    slug: str = Field(min_length=1, max_length=255, description="Уникальный slug для приглашения")
    role: WorkspaceMemberRoleEnum = Field(description="Роль, назначаемая при вступлении")
    expired_at: datetime.datetime | None = Field(default=None, description="Дата истечения срока действия")
    is_active: bool | None = Field(default=None, description="Активно ли приглашение")


class WorkspaceJoinRuleRequestCreateDTO(WorkspaceJoinRuleBaseCreateDTO):
    password: str | None = Field(default=None, max_length=255, description="Пароль для вступления")


class WorkspaceJoinRuleRequestUpdateDTO(WorkspaceJoinRuleRequestCreateDTO):
    pass


class WorkspaceJoinRuleCreateDTO(WorkspaceJoinRuleBaseCreateDTO):
    hashed_password: str | None = Field(default=None, max_length=255, description="Пароль для вступления")


class WorkspaceJoinRuleUpdateDTO(WorkspaceJoinRuleCreateDTO):
    pass


class WorkspaceJoinRuleResponseDTO(BaseDTO):
    id: int = Field(description="ID приглашения")
    workspace_id: int = Field(description="ID рабочего пространства")
    slug: str = Field(description="Уникальный slug для приглашения")
    role: WorkspaceMemberRoleEnum = Field(description="Роль, назначаемая при вступлении")
    expired_at: datetime.datetime | None = Field(description="Дата истечения срока действия")
    is_active: bool = Field(description="Активно ли приглашение")
    hashed_password: str | None = Field(exclude=True, description="Хеш пароля (исключён из API ответа)")
