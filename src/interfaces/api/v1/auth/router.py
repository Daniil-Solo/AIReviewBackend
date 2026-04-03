from fastapi import APIRouter

from src.application.auth import auth as auth_service
from src.dto.auth.token import TokenDTO, UserLoginDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenDTO)
async def login(
    data: UserLoginDTO,
) -> TokenDTO:
    return await auth_service.login(data)
