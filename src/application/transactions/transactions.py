from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ForbiddenError
from src.constants.transactions import TransactionTypeEnum
from src.di.container import Container
from src.dto.transactions.transactions import (
    AdminTopUpDTO,
    BalanceResponseDTO,
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = get_logger()


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

    create_data = TransactionCreateDTO(
        **data.model_dump(),
        type=TransactionTypeEnum.ADMIN_TOP_UP,
    )
    async with uow.connection():
        return await uow.transactions.create(create_data)


@inject
async def get_transactions(
    user: ShortUserDTO,
    filters: TransactionFilterDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[TransactionResponseDTO]:
    async with uow.connection():
        return await uow.transactions.get_with_filters(user.id, filters)
