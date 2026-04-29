import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.custom_models import (
    CustomModelDTO,
    CustomModelFiltersDTO,
)
from src.dto.custom_models.custom_models import CustomModelCreateDTO, CustomModelUpdateDTO
from src.infrastructure.dao.custom_models.interface import CustomModelsDAO
from src.infrastructure.sqlalchemy.models import custom_models_table


class SQLAlchemyCustomModelsDAO(CustomModelsDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: CustomModelCreateDTO, created_by: int) -> CustomModelDTO:
        query = (
            sa.insert(custom_models_table)
            .values(
                **data.model_dump(),
                created_by=created_by,
            )
            .returning(custom_models_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Модель не создана")
        return CustomModelDTO.model_validate(row)

    async def get_by_id(self, model_id: int) -> CustomModelDTO:
        query = sa.select(custom_models_table).where(custom_models_table.c.id == model_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Модель не найдена")
        return CustomModelDTO.model_validate(row)

    async def get_list(self, filters: CustomModelFiltersDTO | None = None) -> list[CustomModelDTO]:
        query = sa.select(custom_models_table)
        if filters is not None and filters.workspace_id is not None:
            query = query.where(custom_models_table.c.workspace_id == filters.workspace_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [CustomModelDTO.model_validate(row) for row in rows]

    async def update(self, model_id: int, data: CustomModelUpdateDTO) -> CustomModelDTO:
        query = (
            sa.update(custom_models_table)
            .where(custom_models_table.c.id == model_id)
            .values(**data.model_dump())
            .returning(custom_models_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Модель не найдена")
        return CustomModelDTO.model_validate(row)

    async def delete(self, model_id: int) -> None:
        query = sa.delete(custom_models_table).where(custom_models_table.c.id == model_id)
        await self.session.execute(query)
