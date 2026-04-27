from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

import src.application.criteria as criteria_service
from src.dto.common import SuccessOperationDTO
from src.dto.criteria.criteria import (
    CriterionCreateDTO,
    CriterionFiltersDTO,
    CriterionResponseDTO,
    CriterionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/criteria", tags=["criteria"])


@router.post("/import", response_model=list[CriterionResponseDTO])
async def import_criteria_endpoint(
    file: UploadFile = File(..., media_type="application/json"),
    workspace_id: int | None = Form(default=None),
    task_id: int | None = Form(default=None),
    user: ShortUserDTO = Depends(get_current_user),
) -> list[CriterionResponseDTO]:
    return await criteria_service.import_criteria(file, workspace_id, task_id, user)


@router.post("", response_model=CriterionResponseDTO)
async def create_criterion_endpoint(
    data: CriterionCreateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> CriterionResponseDTO:
    return await criteria_service.create(data, user)


@router.get("", response_model=list[CriterionResponseDTO])
async def list_criteria_endpoint(
    tags: list[str] | None = Query(default=None),
    search: str | None = Query(default=None),
    user: ShortUserDTO = Depends(get_current_user),
) -> list[CriterionResponseDTO]:
    filters = CriterionFiltersDTO(
        tags=tags,
        search=search,
    )
    return await criteria_service.get_list(filters, user)


@router.get("/available_tags", response_model=list[str])
async def get_available_tags_endpoint(
    user: ShortUserDTO = Depends(get_current_user),
) -> list[str]:
    return await criteria_service.get_available_tags(user)


@router.get("/{criterion_id}", response_model=CriterionResponseDTO)
async def get_criterion_endpoint(
    criterion_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> CriterionResponseDTO:
    return await criteria_service.get_one(criterion_id, user)


@router.put("/{criterion_id}", response_model=CriterionResponseDTO)
async def update_criterion_endpoint(
    criterion_id: int,
    data: CriterionUpdateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> CriterionResponseDTO:
    return await criteria_service.update(criterion_id, data, user)


@router.delete("/{criterion_id}", response_model=SuccessOperationDTO)
async def delete_criterion_endpoint(
    criterion_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await criteria_service.delete(criterion_id, user)
    return SuccessOperationDTO(message="Критерий удалён")
