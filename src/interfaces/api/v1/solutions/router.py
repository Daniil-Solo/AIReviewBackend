from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

import src.application.ai_review.pipeline as pipeline_service
import src.application.solutions.review_by_criteria as solution_criteria_checks_service
import src.application.solutions.score as score_service
import src.application.solutions.solutions as solution_service
import src.application.solutions.wind_rose as wind_rose_service
from src.constants.ai_pipeline import PipelineStepEnum
from src.constants.ai_review import SolutionFormatEnum
from src.dto.ai_review.pipeline import PipelineInfoDTO
from src.dto.common import SuccessOperationDTO
from src.dto.solutions.human_grading import CriteriaGradingReviewResponseDTO
from src.dto.solutions.solution_criteria_checks import SolutionCriteriaCheckCreateRequestDTO
from src.dto.solutions.solutions import (
    SolutionCreateRequestDTO,
    SolutionFiltersRequestDTO,
    SolutionFinalReviewDTO,
    SolutionLabelUpdateDTO,
    SolutionShortResponseDTO,
)
from src.dto.solutions.score import SolutionScoreDTO
from src.dto.solutions.wind_rose import WindRosePointDTO
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.post("", response_model=SolutionShortResponseDTO)
async def create_endpoint(
    task_id: Annotated[int, Form()],
    solution_format: Annotated[SolutionFormatEnum, Form()],
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
    github_repo_link: Annotated[str | None, Form()] = None,
    github_repo_branch: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> SolutionShortResponseDTO:
    data = SolutionCreateRequestDTO(
        task_id=task_id,
        format=solution_format,
        github_repo_link=github_repo_link,
        github_repo_branch=github_repo_branch,
    )
    return await solution_service.create(data, file, user)


@router.get("/my", response_model=list[SolutionShortResponseDTO])
async def get_my_solutions_endpoint(
    filters: Annotated[SolutionFiltersRequestDTO, Depends()],
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> list[SolutionShortResponseDTO]:
    return await solution_service.get_my_solutions(filters, user)


@router.get("/{solution_id}", response_model=SolutionShortResponseDTO)
async def get_endpoint(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SolutionShortResponseDTO:
    return await solution_service.get(solution_id, user)


@router.post("/{solution_id}/cancel", response_model=SuccessOperationDTO)
async def cancel_endpoint(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await solution_service.cancel(solution_id, user)
    return SuccessOperationDTO(message="Проверка решения отменена")


@router.post("/{solution_id}/restart", response_model=SuccessOperationDTO)
async def restart_pipeline(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await pipeline_service.restart(solution_id, user)
    return SuccessOperationDTO(message="Пайплайн перезапущен")


@router.get("/{solution_id}/info", response_model=PipelineInfoDTO)
async def get_pipeline_info(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> PipelineInfoDTO:
    return await pipeline_service.get_info(solution_id, user)


@router.get("/{solution_id}/artefacts/{step}")
async def get_artefact_endpoint(
    solution_id: int,
    step: PipelineStepEnum,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> StreamingResponse:
    content = await solution_service.get_artifact(solution_id, step, user)
    return StreamingResponse(
        content=iter([content]),
        media_type="text/plain; charset=utf-8",
    )


@router.post("/{solution_id}/criteria-checks", response_model=SuccessOperationDTO)
async def create_criteria_check_endpoint(
    solution_id: int,
    data: SolutionCriteriaCheckCreateRequestDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await solution_criteria_checks_service.create_criteria_check(solution_id, data, user)
    return SuccessOperationDTO(message="Фидбек оставлен")


@router.get("/{solution_id}/criteria-checks", response_model=CriteriaGradingReviewResponseDTO)
async def get_criteria_check_endpoint(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> CriteriaGradingReviewResponseDTO:
    return await solution_criteria_checks_service.get_criteria_review(solution_id, user)


@router.get("/{solution_id}/wind-rose", response_model=list[WindRosePointDTO])
async def get_wind_rose_endpoint(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> list[WindRosePointDTO]:
    return await wind_rose_service.get_wind_rose(solution_id, user)


@router.get("/{solution_id}/score", response_model=SolutionScoreDTO)
async def get_score_endpoint(
    solution_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SolutionScoreDTO:
    return await score_service.get_score(solution_id, user)


@router.post("/{solution_id}/final-review", response_model=SolutionShortResponseDTO)
async def final_review_endpoint(
    solution_id: int,
    data: SolutionFinalReviewDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SolutionShortResponseDTO:
    return await solution_service.final_review(solution_id, data, user)


@router.patch("/{solution_id}/label", response_model=SolutionShortResponseDTO)
async def update_label_endpoint(
    solution_id: int,
    data: SolutionLabelUpdateDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SolutionShortResponseDTO:
    return await solution_service.update_label(solution_id, data.label, user)


@router.post("/{solution_id}/approval", response_model=SolutionShortResponseDTO)
async def approve_project_doc_endpoint(
    solution_id: int,
    file: Annotated[UploadFile, File()],
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SolutionShortResponseDTO:
    return await solution_service.approve_project_doc(solution_id, file, user)
