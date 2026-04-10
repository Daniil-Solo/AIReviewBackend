import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.tasks.tasks import (
    TaskCreateDTO,
    TaskFiltersDTO,
    TaskResponseDTO,
    TaskUpdateDTO,
)
from src.infrastructure.dao.tasks.interface import TasksDAO
from src.infrastructure.sqlalchemy.models import tasks_table


class SQLAlchemyTasksDAO(TasksDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TaskCreateDTO, created_by: int) -> TaskResponseDTO:
        query = sa.insert(tasks_table).values(**data.model_dump(), created_by=created_by).returning(tasks_table)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Задача не создана")
        return TaskResponseDTO.model_validate(row)

    async def get_by_id(self, task_id: int) -> TaskResponseDTO:
        query = sa.select(tasks_table).where(tasks_table.c.id == task_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Задача не найдена")
        return TaskResponseDTO.model_validate(row)

    async def update(self, task_id: int, data: TaskUpdateDTO) -> TaskResponseDTO:
        query = (
            sa.update(tasks_table)
            .where(tasks_table.c.id == task_id)
            .values(**data.model_dump(by_alias=True))
            .returning(tasks_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Задача не найдена")
        return TaskResponseDTO.model_validate(row)

    async def get_list(self, filters: TaskFiltersDTO) -> list[TaskResponseDTO]:
        query = sa.select(tasks_table)

        if filters.is_active is not None:
            query = query.where(tasks_table.c.is_active.is_(filters.is_active))

        if filters.workspace_id is not None:
            query = query.where(tasks_table.c.workspace_id == filters.workspace_id)

        result = await self.session.execute(query)
        rows = result.fetchall()
        return [TaskResponseDTO.model_validate(row) for row in rows]

    async def get_public_by_id(self, task_id: int) -> TaskResponseDTO:
        query = sa.select(tasks_table).where(tasks_table.c.id == task_id, tasks_table.c.is_active == sa.true())
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Задача не найдена")
        return TaskResponseDTO.model_validate(row)

    async def delete(self, task_id: int) -> None:
        query = sa.delete(tasks_table).where(tasks_table.c.id == task_id)
        await self.session.execute(query)
