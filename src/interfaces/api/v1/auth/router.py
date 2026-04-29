from fastapi import APIRouter

from src.application.auth.auth import login
from src.application.auth.register import (
    confirm_registration,
    start_registration,
)
from src.dto.auth.auth import TokenDTO, UserLoginDTO
from src.dto.auth.register import (
    EmailConfirmationRequestDTO,
    EmailRegistrationRequestDTO,
)
from src.dto.common import SuccessOperationDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenDTO)
async def login_endpoint(data: UserLoginDTO) -> TokenDTO:
    return await login(data)


@router.post("/register/start", response_model=SuccessOperationDTO)
async def start_registration_endpoint(
    data: EmailRegistrationRequestDTO,
) -> SuccessOperationDTO:
    return await start_registration(data=data)


@router.post("/register/confirm", response_model=TokenDTO)
async def confirm_registration_endpoint(data: EmailConfirmationRequestDTO) -> TokenDTO:
    return await confirm_registration(data)
