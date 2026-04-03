from fastapi import APIRouter, Depends

from src.dto.users.user import UserResponseDTO, ShortUserDTO
from src.interfaces.api.dependencies import get_current_user
from src.application.users import users as users_service


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponseDTO])
async def get_users(
    user:  ShortUserDTO = Depends(get_current_user),  # noqa: B008, ARG001
) -> list[UserResponseDTO]:
    return await users_service.get_all_users(user)
