from dependency_injector.wiring import inject, Provide

from src.application.ai_review.task_graph import ALL_STEPS
from src.application.exceptions import ForbiddenError
from src.application.workspaces.common import check_member_role
from src.constants.ai_review import SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.ai_review.pipeline import PipelineInfoDTO
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork

logger = get_logger()


@inject
async def start(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)
        task = await uow.tasks.get_by_id(solution.task_id)
        member = await check_member_role(uow, user.id, task.workspace_id)
        if solution.created_by != user.id and member.role not in {
            WorkspaceMemberRoleEnum.OWNER,
            WorkspaceMemberRoleEnum.TEACHER,
        }:
            raise ForbiddenError(message="Пользователь не имеет доступ к этому решению")

        await uow.solutions.update(
            solution_id,
            SolutionUpdateDTO(status=SolutionStatusEnum.AI_REVIEW, steps=[]),
        )
        await uow.pipeline_tasks.create_tasks(solution_id, ALL_STEPS)


@inject
async def restart(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)
        task = await uow.tasks.get_by_id(solution.task_id)
        member = await check_member_role(uow, user.id, task.workspace_id)
        if solution.created_by != user.id and member.role not in {
            WorkspaceMemberRoleEnum.OWNER,
            WorkspaceMemberRoleEnum.TEACHER,
        }:
            raise ForbiddenError(message="Пользователь не имеет доступ к этому решению")

        solution = await uow.solutions.get_by_id(solution_id)
        await uow.pipeline_tasks.delete_solution_tasks(solution_id)
        await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=SolutionStatusEnum.AI_REVIEW, steps=[]),
        )
        await uow.pipeline_tasks.create_tasks(solution_id, ALL_STEPS)


@inject
async def get_info(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> PipelineInfoDTO:
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        task = await uow.tasks.get_by_id(solution.task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        pipeline_tasks = await uow.pipeline_tasks.get_solution_tasks(solution_id)
    return PipelineInfoDTO(
        solution_id=solution.id,
        solution_status=solution.status,
        solution_steps=solution.steps,
        pipeline_tasks=pipeline_tasks,
    )
