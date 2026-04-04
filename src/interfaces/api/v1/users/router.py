from fastapi import APIRouter, Depends

from src.application.users.users import create_admin, create_user, get_all_users, get_user
from src.dto.users.user import ShortUserDTO, UserCreateDTO, UserResponseDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponseDTO])
async def get_users(
    user: ShortUserDTO = Depends(get_current_user),  # noqa: B008
) -> list[UserResponseDTO]:
    return await get_all_users(user)


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user_endpoint(user_id: int) -> UserResponseDTO:
    return await get_user(user_id)


@router.post("/", response_model=UserResponseDTO)
async def create_user_endpoint(data: UserCreateDTO) -> UserResponseDTO:
    return await create_user(data)


@router.post("/admin", response_model=UserResponseDTO)
async def create_admin_endpoint(data: UserCreateDTO) -> UserResponseDTO:
    return await create_admin(data)
