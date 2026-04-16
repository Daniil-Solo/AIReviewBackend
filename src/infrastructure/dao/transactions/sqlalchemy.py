import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto.transactions.transactions import (
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionResponseDTO,
)
from src.infrastructure.dao.transactions.interface import TransactionsDAO
from src.infrastructure.sqlalchemy.models import transactions_table


class SQLAlchemyTransactionsDAO(TransactionsDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TransactionCreateDTO) -> TransactionResponseDTO:
        query = sa.insert(transactions_table).values(**data.model_dump(by_alias=True)).returning(transactions_table)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise Exception("Транзакция не создана")
        return TransactionResponseDTO.model_validate(row)

    async def get_by_user_id(self, user_id: int, limit: int = 100) -> list[TransactionResponseDTO]:
        query = (
            sa.select(transactions_table)
            .where(transactions_table.c.user_id == user_id)
            .order_by(transactions_table.c.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [TransactionResponseDTO.model_validate(row) for row in rows]

    async def get_balance_by_user_id(self, user_id: int) -> float:
        query = sa.select(sa.func.sum(transactions_table.c.amount)).where(transactions_table.c.user_id == user_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None or row[0] is None:
            return 0.0
        return float(row[0])

    async def get_with_filters(self, user_id: int, filters: TransactionFilterDTO) -> list[TransactionResponseDTO]:
        conditions = [transactions_table.c.user_id == user_id]

        if filters.started_at is not None:
            conditions.append(transactions_table.c.created_at >= filters.started_at)

        if filters.ended_at is not None:
            conditions.append(transactions_table.c.created_at <= filters.ended_at)

        if filters.types is not None and len(filters.types) > 0:
            conditions.append(transactions_table.c.type.in_([str(t) for t in filters.types]))

        query = sa.select(transactions_table).where(*conditions).order_by(transactions_table.c.created_at.desc())
        result = await self.session.execute(query)
        rows = result.fetchall()

        return [TransactionResponseDTO.model_validate(row) for row in rows]
