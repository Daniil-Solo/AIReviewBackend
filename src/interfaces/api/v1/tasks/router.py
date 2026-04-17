from fastapi import APIRouter, Depends

import src.application.solutions.solutions as solution_service
import src.application.tasks as task_service
import src.application.tasks.task_criteria as task_criteria_service
from src.dto.common import SuccessOperationDTO
from src.dto.solutions.solutions import SolutionShortResponseDTO
from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateDTO,
    TaskCriteriaResponseDTO,
    TaskCriteriaUpdateWeightDTO,
    TaskCriteriaCreateRequestDTO, TaskCriteriaFullResponseDTO, TaskCriteriaCreateBatchDTO,
)
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


@router.delete("/{task_id}", response_model=SuccessOperationDTO)
async def delete_endpoint(
    task_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await task_service.delete(task_id, user)
    return SuccessOperationDTO(message="Задача удалена")


@router.post("/{task_id}/criteria", response_model=TaskCriteriaResponseDTO)
async def create_criterion_endpoint(
    task_id: int,
    data: TaskCriteriaCreateRequestDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskCriteriaResponseDTO:
    data = TaskCriteriaCreateDTO(**data.model_dump(), task_id=task_id)
    return await task_criteria_service.create(data, user)


@router.post("/{task_id}/criteria/batch", response_model=SuccessOperationDTO)
async def create_criteria_batch_endpoint(
    task_id: int,
    data: TaskCriteriaCreateBatchDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await task_criteria_service.create_batch(task_id, data, user)
    return SuccessOperationDTO(message="Критерии прикреплены к задаче")


@router.get("/{task_id}/criteria", response_model=list[TaskCriteriaFullResponseDTO])
async def get_criteria_endpoint(
    task_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> list[TaskCriteriaResponseDTO]:
    return await task_criteria_service.get_by_task(task_id, user)


@router.patch("/{task_id}/criteria/{task_criterion_id}", response_model=TaskCriteriaResponseDTO)
async def update_criterion_endpoint(
    task_id: int,
    task_criterion_id: int,
    data: TaskCriteriaUpdateWeightDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> TaskCriteriaResponseDTO:
    return await task_criteria_service.update(task_criterion_id, data, user)


@router.delete("/{task_id}/criteria/{task_criterion_id}", response_model=SuccessOperationDTO)
async def delete_criterion_endpoint(
    task_id: int,
    task_criterion_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await task_criteria_service.delete(task_criterion_id, user)
    return SuccessOperationDTO(message="Критерий задачи удален")


@router.get("/{task_id}/solutions", response_model=list[SolutionShortResponseDTO])
async def get_list_by_task_endpoint(
    task_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> list[SolutionShortResponseDTO]:
    return await solution_service.get_list_by_task(task_id, user)
