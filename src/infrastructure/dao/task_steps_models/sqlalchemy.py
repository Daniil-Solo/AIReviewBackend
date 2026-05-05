import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.custom_models import TaskStepsModelDTO
from src.dto.custom_models.custom_models import TaskStepsModelUpsertDTO
from src.infrastructure.dao.task_steps_models.interface import TaskStepsModelsDAO
from src.infrastructure.sqlalchemy.models import task_steps_models_table, tasks_table


class SQLAlchemyTaskStepsModelsDAO(TaskStepsModelsDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, data: TaskStepsModelUpsertDTO) -> TaskStepsModelDTO:
        stmt = (
            pg_insert(task_steps_models_table)
            .values(task_id=data.task_id, steps=data.steps)
            .on_conflict_do_update(index_elements=[task_steps_models_table.c.task_id], set_={"steps": data.steps})
            .returning(task_steps_models_table)
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Запись не создана")
        return TaskStepsModelDTO.model_validate(row)

    async def get(self, task_id: int) -> TaskStepsModelDTO | None:
        query = sa.select(task_steps_models_table).where(task_steps_models_table.c.task_id == task_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Запись не найдена")
        return TaskStepsModelDTO.model_validate(row)

    async def clear_model_references(self, workspace_id: int, model_id: int) -> None:
        subquery = sa.select(tasks_table.c.id).where(tasks_table.c.workspace_id == workspace_id).subquery()
        select_query = sa.select(task_steps_models_table).where(
            task_steps_models_table.c.task_id.in_(sa.select(subquery))
        )
        result = await self.session.execute(select_query)
        rows = result.fetchall()

        for row in rows:
            steps = row.steps
            updated = False
            for step_name, step_model_id in steps.items():
                if step_model_id == model_id:
                    steps[step_name] = None
                    updated = True
            if updated:
                update_query = (
                    sa.update(task_steps_models_table).where(task_steps_models_table.c.id == row.id).values(steps=steps)
                )
                await self.session.execute(update_query)
