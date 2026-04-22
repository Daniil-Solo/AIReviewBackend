from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO, TaskCriteriaResponseDTO
from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.tasks import TaskFactory, TaskUpdateFactory


async def create_task(
    uow: UnitOfWork, workspace_id: int, user_id: int, is_active: bool | None = None
) -> TaskResponseDTO:
    data: TaskCreateDTO = TaskFactory.build(workspace_id=workspace_id)
    async with uow.connection():
        task = await uow.tasks.create(data, created_by=user_id)
        if is_active is not None:
            await uow.tasks.update(
                task.id, TaskUpdateFactory.build(name=task.name, description=task.description, is_active=is_active)
            )
        return task


async def create_task_criterion(
    uow: UnitOfWork,
    task_id: int,
    criterion_id: int,
    weight: float = 1.0,
) -> TaskCriteriaResponseDTO:
    data = TaskCriteriaCreateDTO(
        task_id=task_id,
        criterion_id=criterion_id,
        weight=weight,
    )
    async with uow.connection():
        return await uow.task_criteria.create(data)
