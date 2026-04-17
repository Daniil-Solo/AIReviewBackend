from fastapi import APIRouter, Depends

from src.application.workspaces import get_user_workspaces
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.workspace import UserWorkspaceResponseDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/workspaces", response_model=list[UserWorkspaceResponseDTO])
async def get_profile_workspaces_endpoint(
    user: ShortUserDTO = Depends(get_current_user),
) -> list[UserWorkspaceResponseDTO]:
    return await get_user_workspaces(user)
