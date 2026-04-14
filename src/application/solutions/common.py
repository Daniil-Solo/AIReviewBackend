from src.application.exceptions import ForbiddenError
from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.solutions.solutions import SolutionResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def check_solution_permissions(
    uow: UnitOfWork,
    user_id: int,
    solution_id: int,
    allow_author: bool = True
) -> SolutionResponseDTO:
    solution = await uow.solutions.get_by_id(solution_id)
    task = await uow.tasks.get_by_id(solution.task_id)
    member = await check_member_role(uow, user_id, task.workspace_id)

    allowed_roles = {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
    if member.role in allowed_roles:
        return solution

    if allow_author and solution.created_by == user_id:
        return solution

    raise ForbiddenError(message="Пользователь не имеет доступ к этому решению")
