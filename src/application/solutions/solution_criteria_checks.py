from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.ai_review import CriterionCheckStatusEnum, CriterionStageEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.solutions.solution_criteria_checks import (
    SolutionCriteriaCheckCreateDTO,
    SolutionCriteriaCheckCreateRequestDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create_criteria_check(
    solution_id: int,
    data: SolutionCriteriaCheckCreateRequestDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    solution = await uow.solutions.get_by_id(solution_id)
    task = await uow.tasks.get_by_id(solution.task_id)

    await check_member_role(
        uow,
        user.id,
        task.workspace_id,
        allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
    )

    await uow.solution_criteria_checks.create(
        SolutionCriteriaCheckCreateDTO(
            task_criterion_id=data.task_criterion_id,
            solution_id=solution_id,
            comment=data.comment,
            stage=CriterionStageEnum.MANUAL,
            status=CriterionCheckStatusEnum.SUFFICIENT,
            is_passed=data.is_passed,
        )
    )
