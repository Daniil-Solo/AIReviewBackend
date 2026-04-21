import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.solutions.solution_criteria_checks import (
    SolutionCriteriaCheckCreateDTO,
    SolutionCriteriaCheckFiltersDTO,
    SolutionCriteriaCheckResponseDTO,
)
from src.infrastructure.dao.solution_criteria_checks.interface import SolutionCriteriaChecksDAO
from src.infrastructure.sqlalchemy.models import solution_criteria_checks_table


class SQLAlchemySolutionCriteriaChecksDAO(SolutionCriteriaChecksDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, filters: SolutionCriteriaCheckFiltersDTO) -> list[SolutionCriteriaCheckResponseDTO]:
        query = sa.select(solution_criteria_checks_table)
        if filters.task_criterion_id is not None:
            query = query.where(solution_criteria_checks_table.c.task_criterion_id == filters.task_criterion_id)
        if filters.solution_id is not None:
            query = query.where(solution_criteria_checks_table.c.solution_id == filters.solution_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [SolutionCriteriaCheckResponseDTO.model_validate(row) for row in rows]

    async def create(self, data: SolutionCriteriaCheckCreateDTO) -> SolutionCriteriaCheckResponseDTO:
        query = (
            sa.insert(solution_criteria_checks_table)
            .values(**data.model_dump(by_alias=True))
            .returning(solution_criteria_checks_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Проверка критерия не создана")
        return SolutionCriteriaCheckResponseDTO.model_validate(row)
