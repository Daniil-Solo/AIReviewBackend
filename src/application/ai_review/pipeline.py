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
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = get_logger()

RESTART_ALLOWED_STATUSES = {SolutionStatusEnum.ERROR, SolutionStatusEnum.CANCELLED, SolutionStatusEnum.REVIEWED}


@inject
async def restart(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)

        if solution.status not in RESTART_ALLOWED_STATUSES:
            raise ApplicationError(
                message="Перезапуск проверки доступен только в случае ошибки, отмены проверки или после AI-проверки",
                code="solution_status_invalid",
            )

        task = await uow.tasks.get_by_id(solution.task_id)
        await check_member_role(
            uow, user.id, task.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )

        await uow.pipeline_tasks.delete_many(solution.id)
        await uow.solutions.delete_by_solution_id(solution.id)
        await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=SolutionStatusEnum.AI_REVIEW, steps=[]),
        )
        await uow.pipeline_tasks.create_many(solution_id, ALL_STEPS)


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
