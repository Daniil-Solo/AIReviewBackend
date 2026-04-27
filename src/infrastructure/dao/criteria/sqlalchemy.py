import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.criteria.criteria import (
    CriterionCreateDTO,
    CriterionFiltersDTO,
    CriterionResponseDTO,
    CriterionUpdateDTO,
)
from src.infrastructure.dao.criteria.interface import CriteriaDAO
from src.infrastructure.sqlalchemy.models import criteria_table


class SQLAlchemyCriteriaDAO(CriteriaDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: CriterionCreateDTO, created_by: int) -> CriterionResponseDTO:
        query = (
            sa.insert(criteria_table)
            .values(
                **data.model_dump(by_alias=True),
                created_by=created_by,
            )
            .returning(criteria_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Критерий не создан")
        return CriterionResponseDTO.model_validate(row)

    async def get_by_id(self, criterion_id: int) -> CriterionResponseDTO:
        query = sa.select(criteria_table).where(criteria_table.c.id == criterion_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Критерий не найден")
        return CriterionResponseDTO.model_validate(row)

    async def get_list(self, filters: CriterionFiltersDTO) -> list[CriterionResponseDTO]:
        query = sa.select(criteria_table)

        if filters.tags is not None:
            tag_conditions = [criteria_table.c.tags.any(tag) for tag in filters.tags]
            query = query.where(sa.or_(*tag_conditions))
        if filters.search is not None:
            query = query.where(criteria_table.c.description.ilike(f"%{filters.search}%"))

        level_conditions = []

        if filters.workspace_id is not None:
            level_conditions.append(criteria_table.c.workspace_id == filters.workspace_id)
        if filters.task_id is not None:
            level_conditions.append(criteria_table.c.task_id == filters.task_id)

        level_conditions.append(
            sa.and_(
                criteria_table.c.workspace_id.is_(None),
                criteria_table.c.task_id.is_(None),
            )
        )

        query = query.where(sa.or_(*level_conditions))

        result = await self.session.execute(query)
        rows = result.fetchall()
        return [CriterionResponseDTO.model_validate(row) for row in rows]

    async def get_workspace_criteria(
        self, workspace_id: int, filters: CriterionFiltersDTO
    ) -> list[CriterionResponseDTO]:
        query = sa.select(criteria_table).where(
            criteria_table.c.workspace_id == workspace_id,
        )
        if filters.tags is not None:
            tag_conditions = [criteria_table.c.tags.any(tag) for tag in filters.tags]
            query = query.where(sa.or_(*tag_conditions))
        if filters.search is not None:
            query = query.where(criteria_table.c.description.ilike(f"%{filters.search}%"))

        result = await self.session.execute(query)
        rows = result.fetchall()
        return [CriterionResponseDTO.model_validate(row) for row in rows]

    async def update(self, criterion_id: int, data: CriterionUpdateDTO) -> CriterionResponseDTO:
        query = (
            sa.update(criteria_table)
            .where(criteria_table.c.id == criterion_id)
            .values(**data.model_dump(by_alias=True))
            .returning(criteria_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Критерий не найден")
        return CriterionResponseDTO.model_validate(row)

    async def delete(self, criterion_id: int) -> None:
        query = sa.delete(criteria_table).where(criteria_table.c.id == criterion_id)
        await self.session.execute(query)

    async def get_available_tags(self) -> list[str]:
        query = (
            sa.select(sa.distinct(sa.func.unnest(criteria_table.c.tags)).label("tag"))
            .where(
                criteria_table.c.workspace_id.is_(None),
                criteria_table.c.task_id.is_(None),
            )
            .order_by("tag")
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [row.tag for row in rows]

    async def create_batch(self, data: list[CriterionCreateDTO], created_by: int) -> list[CriterionResponseDTO]:
        if not data:
            return []

        values = [{**d.model_dump(by_alias=True), "created_by": created_by} for d in data]
        query = sa.insert(criteria_table).values(values).returning(criteria_table)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [CriterionResponseDTO.model_validate(row) for row in rows]
