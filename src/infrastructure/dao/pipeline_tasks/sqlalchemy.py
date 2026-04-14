import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dao.pipeline_tasks.interface import (
    PipelineTaskDTO,
    PipelineTasksDAO,
    PipelineTaskStatusEnum,
)
from src.infrastructure.sqlalchemy.models import pipeline_tasks_table


class SQLAlchemyPipelineTasksDAO(PipelineTasksDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_tasks(self, solution_id: int, steps: list[str]) -> list[PipelineTaskDTO]:
        values = [{"solution_id": solution_id, "step": step} for step in steps]
        query = sa.insert(pipeline_tasks_table).values(values).returning(pipeline_tasks_table)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [PipelineTaskDTO.model_validate(row) for row in rows]

    async def get_pending_task(self) -> PipelineTaskDTO | None:
        query = (
            sa.select(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.status == PipelineTaskStatusEnum.PENDING)
            .order_by(pipeline_tasks_table.c.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            return None
        return PipelineTaskDTO.model_validate(row)

    async def mark_running(self, task_id: int) -> PipelineTaskDTO | None:
        query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.id == task_id)
            .where(pipeline_tasks_table.c.status == PipelineTaskStatusEnum.PENDING)
            .values(status=PipelineTaskStatusEnum.RUNNING)
            .returning(pipeline_tasks_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            return None
        return PipelineTaskDTO.model_validate(row)

    async def mark_completed(self, task_id: int) -> PipelineTaskDTO:
        query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.id == task_id)
            .values(status=PipelineTaskStatusEnum.COMPLETED)
            .returning(pipeline_tasks_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        return PipelineTaskDTO.model_validate(row)

    async def mark_completed_task(self, solution_id: int, step: str) -> None:
        query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.solution_id == solution_id)
            .where(pipeline_tasks_table.c.step == step)
            .values(status=PipelineTaskStatusEnum.COMPLETED)
        )
        await self.session.execute(query)

    async def mark_failed(self, task_id: int, error_text: str) -> PipelineTaskDTO:
        query = (
            sa.update(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.id == task_id)
            .values(status=PipelineTaskStatusEnum.FAILED, error_text=error_text)
            .returning(pipeline_tasks_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        return PipelineTaskDTO.model_validate(row)

    async def get_completed_steps(self, solution_id: int) -> list[str]:
        query = (
            sa.select(pipeline_tasks_table.c.step)
            .where(pipeline_tasks_table.c.solution_id == solution_id)
            .where(pipeline_tasks_table.c.status == PipelineTaskStatusEnum.COMPLETED)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [row[0] for row in rows]

    async def get_solution_tasks(self, solution_id: int) -> list[PipelineTaskDTO]:
        query = (
            sa.select(pipeline_tasks_table)
            .where(pipeline_tasks_table.c.solution_id == solution_id)
            .order_by(pipeline_tasks_table.c.created_at)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [PipelineTaskDTO.model_validate(row) for row in rows]

    async def delete_solution_tasks(self, solution_id: int) -> None:
        query = sa.delete(pipeline_tasks_table).where(pipeline_tasks_table.c.solution_id == solution_id)
        await self.session.execute(query)

    async def update_task_status(self, task_id: int, status: PipelineTaskStatusEnum) -> None:
        query = sa.update(pipeline_tasks_table).where(pipeline_tasks_table.c.id == task_id).values(status=status)
        await self.session.execute(query)
