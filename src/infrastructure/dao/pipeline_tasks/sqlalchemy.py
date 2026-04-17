import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.constants.ai_pipeline import PipelineStepEnum, PipelineTaskStatusEnum
from src.dto.ai_review.pipeline import (
    PipelineTaskDTO,
    PipelineTaskFiltersDTO,
    PipelineTaskUpdateDTO,
)
from src.infrastructure.dao.pipeline_tasks.interface import PipelineTasksDAO
from src.infrastructure.sqlalchemy.models import pipeline_tasks_table


class SQLAlchemyPipelineTasksDAO(PipelineTasksDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, solution_id: int, steps: list[PipelineStepEnum]) -> list[PipelineTaskDTO]:
        values = [{"solution_id": solution_id, "step": str(step)} for step in steps]
        query = sa.insert(pipeline_tasks_table).values(values).returning(pipeline_tasks_table)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [PipelineTaskDTO.model_validate(row) for row in rows]

    async def get_ready_pending(self) -> PipelineTaskDTO | None:
        query = (
            sa.select(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.status == str(PipelineTaskStatusEnum.PENDING))
            .order_by(pipeline_tasks_table.c.last_checked_at.nullsfirst(), pipeline_tasks_table.c.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            return None
        return PipelineTaskDTO.model_validate(row)

    async def update_last_checked_at(self, task_id: int) -> None:
        query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.id == task_id)
            .values(last_checked_at=sa.func.now())
        )
        await self.session.execute(query)

    async def update(self, task_id: int, data: PipelineTaskUpdateDTO) -> PipelineTaskDTO:
        update_query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.id == task_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(pipeline_tasks_table)
        )
        result = await self.session.execute(update_query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Задача не найдена")
        return PipelineTaskDTO.model_validate(row)

    async def get_many(self, filters: PipelineTaskFiltersDTO) -> list[PipelineTaskDTO]:
        query = sa.select(pipeline_tasks_table).order_by(pipeline_tasks_table.c.ran_at)

        if filters.solution_id is not None:
            query = query.where(pipeline_tasks_table.c.solution_id == filters.solution_id)

        result = await self.session.execute(query)
        rows = result.fetchall()
        return [PipelineTaskDTO.model_validate(row) for row in rows]

    async def delete_many(self, solution_id: int) -> None:
        query = sa.delete(pipeline_tasks_table).where(pipeline_tasks_table.c.solution_id == solution_id)
        await self.session.execute(query)

    async def delete_many_not_completed(self, solution_id: int) -> None:
        query = sa.delete(pipeline_tasks_table).where(
            pipeline_tasks_table.c.solution_id == solution_id,
            pipeline_tasks_table.c.status != str(PipelineTaskStatusEnum.COMPLETED),
        )
        await self.session.execute(query)
