from src.application.exceptions import EntityNotFoundError, ForbiddenError
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.member import WorkspaceMemberResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def check_member_role(
    uow: UnitOfWork,
    user_id: int,
    workspace_id: int,
    allowed_roles: set[WorkspaceMemberRoleEnum] | None = None,
) -> WorkspaceMemberResponseDTO:
    try:
        member = await uow.workspace_members.get_by_user_and_workspace(user_id, workspace_id)
    except EntityNotFoundError as ex:
        raise ForbiddenError(message="Пользователь не является участником пространства", code="user_not_member") from ex

    if allowed_roles and member.role not in allowed_roles:
        raise ForbiddenError(
            message="Для операции у текущей роли в пространстве недостаточно прав", code="role_permissions"
        )

    return member
