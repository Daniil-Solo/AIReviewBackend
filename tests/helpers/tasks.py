from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def create_task(
    uow: UnitOfWork,
    user_id: int,
    workspace_id: int,
    name: str | None = None,
    description: str | None = None,
    is_active: bool = True,
    use_exam: bool = False,
) -> TaskResponseDTO:
    data = TaskCreateDTO(
        workspace_id=workspace_id,
        name=name or "Test Task",
        description=description or "",
    )
    async with uow.connection():
        task = await uow.tasks.create(data, created_by=user_id)
        if not is_active or use_exam:
            from src.dto.tasks.tasks import TaskUpdateDTO

            update_data = TaskUpdateDTO(
                name=task.name,
                description=task.description,
                is_active=is_active,
            )
            task = await uow.tasks.update(task.id, update_data)
        return task
