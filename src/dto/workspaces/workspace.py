import datetime

from pydantic import Field

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.common import BaseDTO


class WorkspaceCreateDTO(BaseDTO):
    name: str = Field(min_length=1, max_length=255, description="Название рабочего пространства")
    description: str = Field(default="", max_length=5000, description="Описание рабочего пространства")


class WorkspaceUpdateDTO(WorkspaceCreateDTO):
    pass


class WorkspaceResponseDTO(BaseDTO):
    id: int
    name: str = Field(description="Название рабочего пространства")
    description: str = Field(description="Описание рабочего пространства")
    is_archived: bool = Field(description="Флаг архивации")
    created_at: datetime.datetime = Field(description="Дата создания")


class UserWorkspaceResponseDTO(BaseDTO):
    workspace: WorkspaceResponseDTO
    role: WorkspaceMemberRoleEnum = Field(description="Роль пользователя в пространстве")
