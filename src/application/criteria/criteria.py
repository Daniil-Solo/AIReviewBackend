from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ForbiddenError
from src.di.container import Container
from src.dto.criteria.criteria import (
    CriterionCreateDTO,
    CriterionFiltersDTO,
    CriterionResponseDTO,
    CriterionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create(
    data: CriterionCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        return await uow.criteria.create(data, created_by=user.id)


@inject
async def get_one(
    criterion_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection():
        criterion = await uow.criteria.get_by_id(criterion_id)
        if not criterion.is_public and criterion.created_by != user.id:
            raise ForbiddenError(
                message="Просмотр приватного критерия доступен только его автору", code="criterion_access_denied"
            )
        return criterion


@inject
async def get_list(
    filters: CriterionFiltersDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CriterionResponseDTO]:
    async with uow.connection():
        return await uow.criteria.get_list(filters, user.id)


@inject
async def update(
    criterion_id: int,
    data: CriterionUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        criterion = await uow.criteria.get_by_id(criterion_id)
        if criterion.created_by != user.id:
            raise ForbiddenError(
                message="Редактирование критерия доступно только его автору", code="criterion_access_denied"
            )
        return await uow.criteria.update(criterion_id, data)


@inject
async def delete(
    criterion_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        criterion = await uow.criteria.get_by_id(criterion_id)
        if criterion.created_by != user.id:
            raise ForbiddenError(message="Удаление критерия доступно только его автору", code="criterion_access_denied")
        await uow.criteria.delete(criterion_id)


@inject
async def get_available_tags(
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[str]:
    async with uow.connection():
        return await uow.criteria.get_available_tags(user.id)
