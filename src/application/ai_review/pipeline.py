from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError
from src.application.solutions.common import check_solution_permissions
from src.application.workspaces.common import check_member_role
from src.constants.ai_pipeline import ALL_STEPS
from src.constants.ai_review import SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.ai_review.pipeline import PipelineInfoDTO, PipelineTaskFiltersDTO
from src.dto.solutions.solutions import (
    SolutionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings

logger = get_logger()


@inject
async def restart(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)

        task = await uow.tasks.get_by_id(solution.task_id)
        await check_member_role(
            uow, user.id, task.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )

        workspace = await uow.workspaces.get_by_id(task.workspace_id)
        owner_member = (
            await uow.workspace_members.get_list(
                WorkspaceMemberFiltersDTO(workspace_id=workspace.id, roles=[WorkspaceMemberRoleEnum.OWNER])
            )
        )[0]
        balance = await uow.transactions.get_balance_by_user_id(owner_member.user_id)

        await uow.pipeline_tasks.delete_many(solution.id)
        await uow.solutions.delete_by_solution_id(solution.id)
        initial_status = SolutionStatusEnum.PROJECT_GENERATION if not settings.solutions.CHECK_BALANCE_BEFORE_CREATING or balance > 0 else SolutionStatusEnum.ERROR
        await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=initial_status, steps=[]),
        )
        if not settings.solutions.CHECK_BALANCE_BEFORE_CREATING or balance > 0:
            await uow.pipeline_tasks.create_many(solution.id, ALL_STEPS)


@inject
async def get_info(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> PipelineInfoDTO:
    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id, allow_author=False)
        pipeline_tasks = await uow.pipeline_tasks.get_many(PipelineTaskFiltersDTO(solution_id=solution_id))
    return PipelineInfoDTO(
        solution_id=solution.id,
        solution_status=solution.status,
        solution_steps=solution.steps,
        pipeline_tasks=pipeline_tasks,
    )
