from src.constants.ai_review import CriterionCheckStatusEnum, CriterionStageEnum, SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionShortResponseDTO,
    SolutionResponseDTO,
    SolutionUpdateDTO,
)
from src.dto.solutions.solution_criteria_checks import SolutionCriteriaCheckCreateDTO
from src.dto.workspaces.member import WorkspaceMemberCreateDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.solutions import SolutionGitHubFactory
from tests.factories.tasks import TaskFactory
from tests.factories.workspaces import WorkspaceFactory


async def create_github_solution(uow: UnitOfWork, task_id: int, user_id: int) -> SolutionResponseDTO:
    async with uow.connection():
        data = SolutionGitHubFactory.build(task_id=task_id)
        solution = await uow.solutions.create(data, user_id)
        return await uow.solutions.update(solution.id, SolutionUpdateDTO(status=SolutionStatusEnum.PROJECT_GENERATION))


async def create_solution_criteria_check(
    uow: UnitOfWork,
    task_criterion_id: int,
    solution_id: int,
    is_passed: bool,
    status: CriterionCheckStatusEnum = CriterionCheckStatusEnum.SUFFICIENT,
) -> SolutionCriteriaCheckCreateDTO:
    data = SolutionCriteriaCheckCreateDTO(
        task_criterion_id=task_criterion_id,
        solution_id=solution_id,
        stage=CriterionStageEnum.MANUAL,
        status=status,
        is_passed=is_passed,
    )
    async with uow.connection():
        return await uow.solution_criteria_checks.create(data)
