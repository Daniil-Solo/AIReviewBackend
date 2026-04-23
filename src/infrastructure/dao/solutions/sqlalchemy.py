import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.constants.ai_review import SolutionStatusEnum
from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionFiltersDTO,
    SolutionResponseDTO,
    SolutionShortResponseDTO,
    SolutionUpdateDTO,
)
from src.infrastructure.dao.solutions.interface import SolutionsDAO
from src.infrastructure.sqlalchemy.models import solution_criteria_checks_table, solutions_table


class SQLAlchemySolutionsDAO(SolutionsDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: SolutionCreateDTO, created_by: int) -> SolutionResponseDTO:
        query = (
            sa.insert(solutions_table)
            .values(
                **data.model_dump(),
                created_by=created_by,
                status=SolutionStatusEnum.CREATED,
            )
            .returning(solutions_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Решение не создано")
        return SolutionResponseDTO.model_validate(row)

    async def get_by_id(self, solution_id: int) -> SolutionResponseDTO:
        query = sa.select(solutions_table).where(solutions_table.c.id == solution_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Решение не найдено")
        return SolutionResponseDTO.model_validate(row)

    async def update(self, solution_id: int, data: SolutionUpdateDTO) -> SolutionResponseDTO:
        update_values = data.model_dump(by_alias=True, exclude_unset=True)
        if not update_values:
            return await self.get_by_id(solution_id)

        query = (
            sa.update(solutions_table)
            .where(solutions_table.c.id == solution_id)
            .values(**update_values)
            .returning(solutions_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Решение не найдено")
        return SolutionResponseDTO.model_validate(row)

    async def get_list(self, filters: SolutionFiltersDTO | None) -> list[SolutionShortResponseDTO]:
        query = sa.select(solutions_table)
        if filters is not None:
            if filters.created_by is not None:
                query = query.where(solutions_table.c.created_by == filters.created_by)
            if filters.task_id is not None:
                query = query.where(solutions_table.c.task_id == filters.task_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [SolutionShortResponseDTO.model_validate(row) for row in rows]

    async def delete(self, solution_id: int) -> None:
        query = sa.delete(solutions_table).where(solutions_table.c.id == solution_id)
        await self.session.execute(query)

    async def delete_by_solution_id(self, solution_id: int) -> None:
        query = sa.delete(solution_criteria_checks_table).where(
            solution_criteria_checks_table.c.solution_id == solution_id
        )
        await self.session.execute(query)

    async def get_best_grades(self, task_ids: list[int], user_ids: list[int]) -> dict[tuple[int, int], int]:
        if not task_ids:
            return {}

        query = (
            sa.select(
                solutions_table.c.created_by,
                solutions_table.c.task_id,
                sa.func.max(solutions_table.c.human_grade).label("best_grade"),
            )
            .where(
                solutions_table.c.task_id.in_(task_ids),
                solutions_table.c.created_by.in_(user_ids),
            )
            .group_by(solutions_table.c.created_by, solutions_table.c.task_id)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        return {(row.created_by, row.task_id): row.best_grade for row in rows}
