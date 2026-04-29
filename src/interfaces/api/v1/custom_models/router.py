from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.custom_models import (
    delete_custom_model,
    get_custom_model,
    update_custom_model,
)
from src.dto.common import SuccessOperationDTO
from src.dto.custom_models import (
    CustomModelDTO,
    CustomModelRequestUpdateDTO,
    CustomModelWithAPIKeyDTO,
)
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/custom-models", tags=["custom-models"])


@router.get("/{model_id}", response_model=CustomModelWithAPIKeyDTO)
async def get_custom_model_endpoint(
    model_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> CustomModelWithAPIKeyDTO:
    return await get_custom_model(model_id, user)


@router.put("/{model_id}", response_model=CustomModelDTO)
async def update_custom_model_endpoint(
    model_id: int,
    data: CustomModelRequestUpdateDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> CustomModelDTO:
    return await update_custom_model(model_id, data, user)


@router.delete("/{model_id}", response_model=SuccessOperationDTO)
async def delete_custom_model_endpoint(
    model_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await delete_custom_model(model_id, user)
    return SuccessOperationDTO(message="Модель удалена")
