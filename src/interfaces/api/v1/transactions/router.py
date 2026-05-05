from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query

from src.application.transactions.transactions import (
    create_admin_top_up_transaction,
    get_balance,
    get_transactions,
)
from src.constants.transactions import TransactionTypeEnum
from src.dto.transactions.transactions import (
    AdminTopUpDTO,
    BalanceResponseDTO,
    TransactionFilterDTO,
    TransactionResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/balance", response_model=BalanceResponseDTO)
async def get_balance_endpoint(
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> BalanceResponseDTO:
    return await get_balance(user)


@router.post("", response_model=TransactionResponseDTO)
async def create_admin_top_up_transaction_endpoint(
    data: AdminTopUpDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TransactionResponseDTO:
    return await create_admin_top_up_transaction(user, data)


@router.get("", response_model=list[TransactionResponseDTO])
async def get_transactions_endpoint(
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
    started_at: Annotated[datetime | None, Query()] = None,
    ended_at: Annotated[datetime | None, Query()] = None,
    types: Annotated[list[TransactionTypeEnum] | None, Query()] = None,
) -> list[TransactionResponseDTO]:
    filters = TransactionFilterDTO(started_at=started_at, ended_at=ended_at, types=types)
    return await get_transactions(user, filters)
