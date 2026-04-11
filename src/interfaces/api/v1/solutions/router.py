from fastapi import APIRouter, Depends, File, Form, UploadFile

import src.application.solutions.solutions as solution_service
from src.constants.ai_review import SolutionFormatEnum
from src.dto.common import SuccessOperationDTO
from src.dto.solutions.solutions import (
    SolutionCreateRequestDTO,
    SolutionShortResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


solutions_router = APIRouter(prefix="/solutions", tags=["solutions"])


@solutions_router.post("", response_model=SolutionShortResponseDTO)
async def create_endpoint(
    task_id: int = Form(),
    format: SolutionFormatEnum = Form(),
    link: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    user: ShortUserDTO = Depends(get_current_user),
) -> SolutionShortResponseDTO:
    data = SolutionCreateRequestDTO(task_id=task_id, format=format)
    return await solution_service.create(data, file, link, user)


@solutions_router.get("/{solution_id}", response_model=SolutionShortResponseDTO)
async def get_endpoint(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SolutionShortResponseDTO:
    return await solution_service.get(solution_id, user)


@solutions_router.post("/{solution_id}/cancel", response_model=SuccessOperationDTO)
async def cancel_endpoint(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await solution_service.cancel(solution_id, user)
    return SuccessOperationDTO(message="Проверка решения отменена")
