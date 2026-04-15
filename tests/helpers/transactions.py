from src.constants.transactions import TransactionTypeEnum
from src.dto.transactions.transactions import (
    AdminTopUpDTO,
    TransactionCreateDTO,
    TransactionResponseDTO,
)
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def create_transactions(
    uow: UnitOfWork,
    user_id: int,
    size: int = 1,
    amount: float = 1000.0,
    transaction_type: TransactionTypeEnum = TransactionTypeEnum.ADMIN_TOP_UP,
) -> list[TransactionResponseDTO]:
    transactions = []
    async with uow.connection():
        for _ in range(size):
            data = TransactionCreateDTO(
                user_id=user_id,
                amount=amount,
                type=transaction_type,
            )
            transaction = await uow.transactions.create(data)
            transactions.append(transaction)
    return transactions
