from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

import src.application.ai_review.pipeline as pipeline_service
import src.application.solutions.solutions as solution_service
from src.constants.ai_pipeline import PipelineStepEnum
from src.constants.ai_review import SolutionFormatEnum
from src.dto.ai_review.pipeline import PipelineInfoDTO
from src.dto.common import SuccessOperationDTO
from src.dto.solutions.solutions import (
    SolutionCreateRequestDTO,
    SolutionFiltersRequestDTO,
    SolutionShortResponseDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.post("", response_model=SolutionShortResponseDTO)
async def create_endpoint(
    task_id: int = Form(),
    format: SolutionFormatEnum = Form(),
    link: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    user: ShortUserDTO = Depends(get_current_user),
) -> SolutionShortResponseDTO:
    data = SolutionCreateRequestDTO(task_id=task_id, format=format)
    return await solution_service.create(data, file, link, user)


@router.get("/my", response_model=list[SolutionShortResponseDTO])
async def get_my_solutions_endpoint(
    filters: SolutionFiltersRequestDTO = Depends(),
    user: ShortUserDTO = Depends(get_current_user),
) -> list[SolutionShortResponseDTO]:
    return await solution_service.get_my_solutions(filters, user)


@router.get("/{solution_id}", response_model=SolutionShortResponseDTO)
async def get_endpoint(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SolutionShortResponseDTO:
    return await solution_service.get(solution_id, user)


@router.post("/{solution_id}/cancel", response_model=SuccessOperationDTO)
async def cancel_endpoint(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await solution_service.cancel(solution_id, user)
    return SuccessOperationDTO(message="Проверка решения отменена")


@router.post("/{solution_id}/restart", response_model=SuccessOperationDTO)
async def restart_pipeline(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await pipeline_service.restart(solution_id, user)
    return SuccessOperationDTO(message="Пайплайн перезапущен")


@router.get("/{solution_id}/info", response_model=PipelineInfoDTO)
async def get_pipeline_info(
    solution_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> PipelineInfoDTO:
    return await pipeline_service.get_info(solution_id, user)


@router.get("/{solution_id}/artefacts/{step}")
async def get_artefact_endpoint(
    solution_id: int,
    step: PipelineStepEnum,
    user: ShortUserDTO = Depends(get_current_user),
) -> StreamingResponse:
    content = await solution_service.get_artifact(solution_id, step, user)
    return StreamingResponse(
        content=iter([content]),
        media_type="text/plain; charset=utf-8",
    )
