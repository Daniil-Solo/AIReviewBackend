from src.dto.criteria.criteria import CriterionCreateDTO, CriterionResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.criteria import CriterionFactory


async def create_criteria(
    uow: UnitOfWork,
    user_id: int,
    description: str | None = None,
    tags: list[str] | None = None,
    workspace_id: int | None = None,
    task_id: int | None = None,
    size: int = 1,
) -> list[CriterionResponseDTO]:
    initial_data = dict()
    if description is not None:
        initial_data["description"] = description
    if tags is not None:
        initial_data["tags"] = tags
    if workspace_id is not None:
        initial_data["workspace_id"] = workspace_id
    if task_id is not None:
        initial_data["task_id"] = task_id
    data_list = CriterionFactory.build_batch(size=size, **initial_data)
    async with uow.connection():
        return [await uow.criteria.create(data, user_id) for data in data_list]
