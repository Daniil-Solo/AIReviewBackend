from fastapi import APIRouter, HTTPException

from src.application.auth.auth import login
from src.application.auth.register import (
    confirm_registration,
    register_without_confirmation,
    start_registration,
)
from src.constants.emails import EmailSenderTypeEnum
from src.dto.auth.auth import TokenDTO, UserLoginDTO
from src.dto.auth.register import (
    EmailConfirmationRequestDTO,
    EmailRegistrationRequestDTO,
)
from src.dto.common import SuccessOperationDTO
from src.settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenDTO)
async def login_endpoint(data: UserLoginDTO) -> TokenDTO:
    return await login(data)


@router.post("/register/start", response_model=SuccessOperationDTO)
async def start_registration_endpoint(
    data: EmailRegistrationRequestDTO,
) -> SuccessOperationDTO:
    if settings.email.TYPE == EmailSenderTypeEnum.DISABLE:
        raise HTTPException(
            status_code=400,
            detail="Для регистрации используйте POST /api/v1/auth/register",
        )
    return await start_registration(data=data)


@router.post("/register/confirm", response_model=TokenDTO)
async def confirm_registration_endpoint(data: EmailConfirmationRequestDTO) -> TokenDTO:
    if settings.email.TYPE == EmailSenderTypeEnum.DISABLE:
        raise HTTPException(
            status_code=400,
            detail="Для регистрации используйте POST /api/v1/auth/register",
        )
    return await confirm_registration(data)


@router.post("/register", response_model=TokenDTO)
async def register_endpoint(data: EmailRegistrationRequestDTO) -> TokenDTO:
    if settings.email.TYPE != EmailSenderTypeEnum.DISABLE:
        raise HTTPException(
            status_code=400,
            detail="Используйте POST /api/v1/auth/register/start для регистрации с подтверждением по email",
        )
    return await register_without_confirmation(data)
