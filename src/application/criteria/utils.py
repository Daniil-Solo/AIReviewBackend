from src.application.exceptions import ForbiddenError
from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def check_criterion_level_permissions(
    uow: UnitOfWork, user: ShortUserDTO, workspace_id: int | None, task_id: int | None
) -> None:
    if workspace_id is None and task_id is None:
        if not user.is_admin:
            raise ForbiddenError(
                message="Создавать и изменять глобальные критерии могут только администраторы",
                code="criterion_access_denied",
            )
    elif workspace_id is not None:
        await check_member_role(
            uow,
            user.id,
            workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
    elif task_id is not None:
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
