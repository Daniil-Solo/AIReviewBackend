from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ForbiddenError
from src.constants.transactions import TransactionTypeEnum
from src.di.container import Container
from src.dto.transactions.transactions import (
    AdminTopUpDTO,
    BalanceResponseDTO,
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionHourlyGroupDTO,
    TransactionResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def get_balance(
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> BalanceResponseDTO:
    async with uow.connection():
        balance = await uow.transactions.get_balance_by_user_id(user.id)
        return BalanceResponseDTO(balance=balance)


@inject
async def create_admin_top_up_transaction(
    admin: ShortUserDTO,
    data: AdminTopUpDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TransactionResponseDTO:
    if not admin.is_admin:
        raise ForbiddenError(message="Только администратор может создавать транзакции")

    data = TransactionCreateDTO(
        **data.model_dump(),
        type=TransactionTypeEnum.ADMIN_TOP_UP,
    )
    async with uow.connection():
        return await uow.transactions.create(data)


@inject
async def get_transactions(
    user: ShortUserDTO,
    filters: TransactionFilterDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[TransactionHourlyGroupDTO]:
    async with uow.connection():
        return await uow.transactions.get_grouped_by_hour(user.id, filters)
