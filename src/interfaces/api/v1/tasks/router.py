from fastapi import APIRouter, Depends
from pydantic import Field

import src.application.tasks as task_service
from src.dto.common import BaseDTO
from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponseDTO)
async def create_endpoint(
    data: TaskCreateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskResponseDTO:
    return await task_service.create(data, user)


@router.put("/{task_id}", response_model=TaskResponseDTO)
async def update_endpoint(
    task_id: int,
    data: TaskUpdateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskResponseDTO:
    return await task_service.update(task_id, data, user)


@router.get("/{task_id}", response_model=TaskResponseDTO)
async def get_endpoint(
    task_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskResponseDTO:
    return await task_service.get(task_id, user)


@router.get("/{task_id}/public", response_model=TaskResponseDTO)
async def get_public_endpoint(
    task_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskResponseDTO:
    return await task_service.get_public(task_id, user)
