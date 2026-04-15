from datetime import datetime
from typing import Any

from pydantic import Field

from src.constants.transactions import TransactionTypeEnum
from src.dto.common import BaseDTO


class AdminTopUpDTO(BaseDTO):
    user_id: int = Field(description="ID пользователя")
    amount: float = Field(description="Сумма транзакции")


class TransactionCreateDTO(BaseDTO):
    user_id: int = Field(description="ID пользователя")
    amount: float = Field(description="Сумма транзакции")
    type: TransactionTypeEnum = Field(description="Тип транзакции")
    metadata: dict[str, Any] | None = Field(default=None, description="Дополнительные данные")


class TransactionResponseDTO(BaseDTO):
    id: int = Field(description="ID транзакции")
    user_id: int = Field(description="ID пользователя")
    amount: float = Field(description="Сумма транзакции")
    type: TransactionTypeEnum = Field(description="Тип транзакции")
    metadata: dict[str, Any] | None = Field(default=None, description="Дополнительные данные")
    created_at: datetime = Field(description="Дата создания")


class BalanceResponseDTO(BaseDTO):
    balance: float = Field(description="Текущий баланс пользователя")


class TransactionHourlyGroupDTO(BaseDTO):
    hour: datetime = Field(description="Время (час)")
    amount: float = Field(description="Сумма за час")


class TransactionFilterDTO(BaseDTO):
    started_at: datetime | None = Field(default=None, description="Начало периода (UTC)")
    ended_at: datetime | None = Field(default=None, description="Конец периода (UTC)")
