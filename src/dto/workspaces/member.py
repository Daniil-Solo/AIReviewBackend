from pydantic import Field

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.common import BaseDTO


class WorkspaceMemberCreateDTO(BaseDTO):
    user_id: int = Field(description="Идентификатор пользователя")
    workspace_id: int = Field(description="Идентификатор пространства")
    role: WorkspaceMemberRoleEnum = Field(description="Роль участника в пространстве")


class WorkspaceMemberResponseDTO(WorkspaceMemberCreateDTO):
    id: int
    fullname: str = Field(description="Полное имя участника")
    email: str = Field(description="Email участника")


class WorkspaceMemberUpdateDTO(BaseDTO):
    role: WorkspaceMemberRoleEnum = Field(description="Роль участника в пространстве")


class WorkspaceMemberFiltersDTO(BaseDTO):
    workspace_id: int = Field(description="Идентификатор пространства")
    roles: list[WorkspaceMemberRoleEnum] | None = Field(default=None, description="Роли в пространстве")


class TransferOwnershipDTO(BaseDTO):
    member_id: int = Field(description="ID участника, которому передаётся владение")
