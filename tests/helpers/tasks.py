from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.tasks import TaskFactory, TaskUpdateFactory


async def create_task(
    uow: UnitOfWork,
    workspace_id: int,
    user_id: int,
    is_active: bool | None = None
) -> TaskResponseDTO:
    data: TaskCreateDTO = TaskFactory.build(workspace_id=workspace_id)
    async with uow.connection():
        task = await uow.tasks.create(data, created_by=user_id)
        if is_active is not  None:
            await uow.tasks.update(task.id, TaskUpdateFactory.build(name=task.name, description=task.description, is_active=is_active))
        return task
