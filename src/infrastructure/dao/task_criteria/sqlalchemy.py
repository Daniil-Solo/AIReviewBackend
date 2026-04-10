import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateDTO,
    TaskCriteriaResponseDTO,
    TaskCriteriaUpdateWeightDTO,
)
from src.infrastructure.dao.task_criteria.interface import TaskCriteriaDAO
from src.infrastructure.sqlalchemy.models import task_criteria_table


class SQLAlchemyTaskCriteriaDAO(TaskCriteriaDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TaskCriteriaCreateDTO) -> TaskCriteriaResponseDTO:
        query = sa.insert(task_criteria_table).values(**data.model_dump(by_alias=True)).returning(task_criteria_table)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Связка задачи и критерия не создана")
        return TaskCriteriaResponseDTO.model_validate(row)

    async def get_by_id(self, task_criterion_id: int) -> TaskCriteriaResponseDTO:
        query = sa.select(task_criteria_table).where(task_criteria_table.c.id == task_criterion_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Связка задачи и критерия не найдена")
        return TaskCriteriaResponseDTO.model_validate(row)

    async def update(self, task_criterion_id: int, data: TaskCriteriaUpdateWeightDTO) -> TaskCriteriaResponseDTO:
        query = (
            sa.update(task_criteria_table)
            .where(task_criteria_table.c.id == task_criterion_id)
            .values(weight=data.weight)
            .returning(task_criteria_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Связка задачи и критерия не найдена")
        return TaskCriteriaResponseDTO.model_validate(row)

    async def delete(self, task_criterion_id: int) -> None:
        query = sa.delete(task_criteria_table).where(task_criteria_table.c.id == task_criterion_id)
        await self.session.execute(query)

    async def get_by_task_id(self, task_id: int) -> list[TaskCriteriaResponseDTO]:
        query = sa.select(task_criteria_table).where(task_criteria_table.c.task_id == task_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [TaskCriteriaResponseDTO.model_validate(row) for row in rows]
