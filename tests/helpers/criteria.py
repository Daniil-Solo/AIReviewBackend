from src.dto.criteria.criteria import CriterionCreateDTO, CriterionResponseDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.criteria import CriterionFactory


async def create_criteria(
    uow: UnitOfWork,
    user_id: int,
    description: str | None = None,
    tags: list[str] | None = None,
    is_public: bool | None = None,
    size: int = 1,
) -> list[CriterionResponseDTO]:
    initial_data = dict()
    if description is not None:
        initial_data["description"] = description
    if tags is not None:
        initial_data["tags"] = tags
    if is_public is not None:
        initial_data["is_public"] = is_public
    data_list = CriterionFactory.build_batch(size=size, **initial_data)
    async with uow.connection():
        return [await uow.criteria.create(data, user_id) for data in data_list]
