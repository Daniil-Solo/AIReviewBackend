from fastapi import APIRouter

from src.application.auth.auth import login
from src.dto.auth.auth import TokenDTO, UserLoginDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenDTO)
async def login_endpoint(data: UserLoginDTO) -> TokenDTO:
    return await login(data)
