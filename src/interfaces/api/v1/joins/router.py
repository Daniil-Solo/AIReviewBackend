from fastapi import APIRouter, Depends

from src.application.workspaces import (
    join_to_workspace,
)
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces import (
    JoinBySlugDTO,
    JoinResponseDTO,
)
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/joins", tags=["joins"])


@router.post("/", response_model=JoinResponseDTO)
async def join_by_slug_endpoint(
    data: JoinBySlugDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> JoinResponseDTO:
    return await join_to_workspace(data, user)
