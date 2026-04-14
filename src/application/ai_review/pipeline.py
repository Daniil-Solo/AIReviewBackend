from dependency_injector.wiring import Provide, inject

from src.application.solutions.common import check_solution_permissions
from src.constants.ai_pipeline import ALL_STEPS
from src.constants.ai_review import SolutionStatusEnum
from src.di.container import Container
from src.dto.ai_review.pipeline import PipelineInfoDTO, PipelineTaskFiltersDTO
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
        solution = await check_solution_permissions(uow, user.id, solution_id)
        await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=SolutionStatusEnum.AI_REVIEW, steps=[]),
        )
        await uow.pipeline_tasks.create_many(solution.id, ALL_STEPS)


@inject
async def restart(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await check_solution_permissions(uow, user.id, solution_id)
        await uow.pipeline_tasks.delete_many(solution.id)
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
