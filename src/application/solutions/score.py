from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError
from src.application.solutions.common import check_solution_permissions
from src.constants.ai_review import SolutionStatusEnum
from src.di.container import Container
from src.dto.solutions.score import SolutionScoreDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def get_score(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> SolutionScoreDTO:
    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id, allow_author=True)
        if solution.status != SolutionStatusEnum.HUMAN_REVIEW:
            raise ApplicationError(
                message="Расчет баллов возможен только на этап проверки преподавателем", code="solution_status_invalid"
            )

        checks = await uow.solution_criteria_checks.get_latest_by_solution(solution_id)
        if not checks:
            return SolutionScoreDTO(
                score=0,
                total_criteria=0,
                passed_criteria=0,
            )

        task_criterion_ids = [ch.task_criterion_id for ch in checks]
        task_criteria = await uow.task_criteria.get_by_ids(task_criterion_ids)
        task_criterion_to_weight = {tc.id: tc.weight for tc in task_criteria}

        total_weight = 0.0
        passed_weight = 0.0
        total_criteria = 0
        passed_criteria = 0

        for check in checks:
            weight = task_criterion_to_weight.get(check.task_criterion_id, 0.0)
            total_weight += weight
            total_criteria += 1

            if check.is_passed:
                passed_weight += weight
                passed_criteria += 1

        if total_weight == 0:
            score = 0
        else:
            score = round((passed_weight / total_weight) * 100)

        return SolutionScoreDTO(
            score=score,
            total_criteria=total_criteria,
            passed_criteria=passed_criteria,
        )
