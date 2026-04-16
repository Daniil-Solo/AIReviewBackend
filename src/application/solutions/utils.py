from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def get_workspace_id(uow: UnitOfWork, solution_id: int) -> int:
    solution = await uow.solutions.get_by_id(solution_id)
    task = await uow.tasks.get_by_id(solution.task_id)
    return task.workspace_id