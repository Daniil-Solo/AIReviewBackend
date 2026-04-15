from abc import ABC, abstractmethod

from src.dto.transactions.transactions import (
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionHourlyGroupDTO,
    TransactionResponseDTO,
)


class TransactionsDAO(ABC):
    @abstractmethod
    async def create(self, data: TransactionCreateDTO) -> TransactionResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int, limit: int = 100) -> list[TransactionResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance_by_user_id(self, user_id: int) -> float:
        raise NotImplementedError

    @abstractmethod
    async def get_grouped_by_hour(self, user_id: int, filters: TransactionFilterDTO) -> list[TransactionHourlyGroupDTO]:
        raise NotImplementedError
