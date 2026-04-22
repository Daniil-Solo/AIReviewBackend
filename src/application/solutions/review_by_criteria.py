from dependency_injector.wiring import Provide, inject

from src.application.solutions.common import check_solution_permissions
from src.application.workspaces.common import check_member_role
from src.constants.ai_review import CriterionCheckStatusEnum, CriterionStageEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.solutions.human_grading import (
    CriteriaGradingReviewResponseDTO,
    GradingCriterionDTO,
)
from src.dto.solutions.solution_criteria_checks import (
    SolutionCriteriaCheckCreateDTO,
    SolutionCriteriaCheckCreateRequestDTO,
    SolutionCriteriaCheckFiltersDTO,
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
    async with uow.connection():
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


@inject
async def get_criteria_review(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriteriaGradingReviewResponseDTO:
    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id, allow_author=False)

        task = await uow.tasks.get_by_id(solution.task_id)
        task_criteria_list = await uow.task_criteria.get_by_task_id(solution.task_id)

        grading_criteria = []
        for task_criterion in task_criteria_list:
            criterion = await uow.criteria.get_by_id(task_criterion.criterion_id)
            checks = await uow.solution_criteria_checks.get_list(
                SolutionCriteriaCheckFiltersDTO(solution_id=solution_id, task_criterion_id=task_criterion.id)
            )
            grading_criteria.append(
                GradingCriterionDTO(
                    criterion=criterion,
                    task_criterion_id=task_criterion.id,
                    weight=task_criterion.weight,
                    checks=checks,
                )
            )

    return CriteriaGradingReviewResponseDTO(
        solution=solution,
        task=task,
        criteria=grading_criteria,
    )
