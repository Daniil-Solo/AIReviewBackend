from collections import defaultdict

from dependency_injector.wiring import Provide, inject

from src.application.solutions.common import check_solution_permissions
from src.di.container import Container
from src.dto.criteria import CriterionFiltersDTO
from src.dto.solutions.wind_rose import WindRosePointDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def get_wind_rose(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[WindRosePointDTO]:
    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id, allow_author=True)
        task = await uow.tasks.get_by_id(solution.task_id)
        checks = await uow.solution_criteria_checks.get_latest_by_solution(solution_id)
        if not checks:
            return []

        task_criterion_ids = [ch.task_criterion_id for ch in checks]
        task_criteria = await uow.task_criteria.get_by_ids(task_criterion_ids)
        task_criterion_to_criterion = {tc.id: tc.criterion_id for tc in task_criteria}

        criterion_ids = list(task_criterion_to_criterion.values())
        criteria = await uow.criteria.get_list(
            CriterionFiltersDTO(ids=criterion_ids, workspace_id=task.workspace_id, task_id=task.id)
        )
        criteria_tags = {c.id: c.tags for c in criteria}

        tag_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "count": 0})

        for check in checks:
            criterion_id = task_criterion_to_criterion.get(check.task_criterion_id)
            if not criterion_id:
                continue

            for tag in criteria_tags.get(criterion_id, []):
                tag_stats[tag]["passed"] += int(check.is_passed)
                tag_stats[tag]["count"] += 1

        return [
            WindRosePointDTO(
                tag=tag,
                value=int(stats["passed"] / stats["count"] * 100) if stats["count"] else 0.0,
                count=stats["count"],
            )
            for tag, stats in tag_stats.items()
        ]
