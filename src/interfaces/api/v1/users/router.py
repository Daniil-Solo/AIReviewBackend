from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from src.dto.users.user import UserResponseDTO
from src.infrastructure.di.container import Container
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponseDTO])
async def get_users(
    users_service: UserService = Depends(Provide[Container.users_service]),  # noqa: B008
    user: UserResponseDTO = Depends(get_current_user),  # noqa: B008, ARG001
) -> list[UserResponseDTO]:
    return await users_service.get_all_users()
