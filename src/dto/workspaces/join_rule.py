import datetime

from pydantic import Field

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.common import BaseDTO


class WorkspaceJoinRuleBaseCreateDTO(BaseDTO):
    slug: str = Field(min_length=1, max_length=255, description="Уникальный slug для приглашения")
    role: WorkspaceMemberRoleEnum = Field(description="Роль, назначаемая при вступлении")
    is_active: bool = Field(default=True, description="Активно ли приглашение")
    expired_at: datetime.datetime | None = Field(default=None, description="Дата истечения срока действия")


class WorkspaceJoinRuleRequestCreateDTO(WorkspaceJoinRuleBaseCreateDTO):
    password: str | None = Field(default=None, max_length=255, description="Пароль для вступления")


class WorkspaceJoinRuleRequestUpdateDTO(WorkspaceJoinRuleRequestCreateDTO):
    pass


class WorkspaceJoinRuleUpdateDTO(WorkspaceJoinRuleBaseCreateDTO):
    hashed_password: str | None = Field(default=None, max_length=255, description="Пароль для вступления")


class WorkspaceJoinRuleCreateDTO(WorkspaceJoinRuleUpdateDTO):
    workspace_id: int = Field(description="ID рабочего пространства")


class WorkspaceJoinRuleResponseDTO(BaseDTO):
    id: int = Field(description="ID приглашения")
    workspace_id: int = Field(description="ID рабочего пространства")
    slug: str = Field(description="Уникальный slug для приглашения")
    role: WorkspaceMemberRoleEnum = Field(description="Роль, назначаемая при вступлении")
    expired_at: datetime.datetime | None = Field(description="Дата истечения срока действия")
    is_active: bool = Field(description="Активно ли приглашение")
    has_password: bool = Field(description="Есть ли пароль у приглашения")
    used_count: int = Field(description="Число использований")


class WorkspaceJoinRuleFullDTO(BaseDTO):
    id: int = Field(description="ID приглашения")
    workspace_id: int = Field(description="ID рабочего пространства")
    slug: str = Field(description="Уникальный slug для приглашения")
    role: WorkspaceMemberRoleEnum = Field(description="Роль, назначаемая при вступлении")
    expired_at: datetime.datetime | None = Field(description="Дата истечения срока действия")
    is_active: bool = Field(description="Активно ли приглашение")
    hashed_password: str | None = Field(exclude=True, description="Хеш пароля (исключён из API ответа)")
    used_count: int = Field(description="Число использований")

    def to_response(self) -> WorkspaceJoinRuleResponseDTO:
        return WorkspaceJoinRuleResponseDTO(**self.model_dump(), has_password=self.hashed_password is not None)
