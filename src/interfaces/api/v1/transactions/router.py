from fastapi import APIRouter, Depends

from src.application.transactions.transactions import (
    create_admin_top_up_transaction,
    get_balance,
    get_transactions,
)
from src.dto.transactions.transactions import (
    AdminTopUpDTO,
    BalanceResponseDTO,
    TransactionFilterDTO,
    TransactionHourlyGroupDTO,
    TransactionResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/balance", response_model=BalanceResponseDTO)
async def get_balance_endpoint(
    user: ShortUserDTO = Depends(get_current_user),
) -> BalanceResponseDTO:
    return await get_balance(user)


@router.post("", response_model=TransactionResponseDTO)
async def create_admin_top_up_transaction_endpoint(
    data: AdminTopUpDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> TransactionResponseDTO:
    return await create_admin_top_up_transaction(user, data)


@router.get("", response_model=list[TransactionHourlyGroupDTO])
async def get_transactions_endpoint(
    filters: TransactionFilterDTO = Depends(),
    user: ShortUserDTO = Depends(get_current_user),
) -> list[TransactionHourlyGroupDTO]:
    return await get_transactions(user, filters)
