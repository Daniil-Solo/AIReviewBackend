from typing import Annotated

from fastapi import APIRouter, Depends, Query

import src.application.criteria.criteria as criteria_service
from src.application.custom_models import (
    get_task_steps_model,
    set_task_steps_model,
)
import src.application.solutions.solutions as solution_service
import src.application.tasks as task_service
import src.application.tasks.task_criteria as task_criteria_service
from src.dto.common import SuccessOperationDTO
from src.dto.criteria import CriterionFiltersDTO, CriterionResponseDTO
from src.dto.custom_models import (
    TaskStepsModelDTO,
    TaskStepsModelRequestCreateDTO,
)
from src.dto.solutions.solutions import SolutionShortResponseDTO
from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateBatchDTO,
    TaskCriteriaCreateDTO,
    TaskCriteriaCreateRequestDTO,
    TaskCriteriaFullResponseDTO,
    TaskCriteriaResponseDTO,
    TaskCriteriaUpdateWeightDTO,
)
from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
from src.dto.users.user import ShortUserDTO
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponseDTO)
async def create_endpoint(
    data: TaskCreateDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskResponseDTO:
    return await task_service.create(data, user)


@router.put("/{task_id}", response_model=TaskResponseDTO)
async def update_endpoint(
    task_id: int,
    data: TaskUpdateDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskResponseDTO:
    return await task_service.update(task_id, data, user)


@router.get("/{task_id}", response_model=TaskResponseDTO)
async def get_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskResponseDTO:
    return await task_service.get(task_id, user)


@router.get("/{task_id}/public", response_model=TaskResponseDTO)
async def get_public_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskResponseDTO:
    return await task_service.get_public(task_id, user)


@router.delete("/{task_id}", response_model=SuccessOperationDTO)
async def delete_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await task_service.delete(task_id, user)
    return SuccessOperationDTO(message="Задача удалена")


@router.post("/{task_id}/criteria", response_model=TaskCriteriaResponseDTO)
async def create_criterion_endpoint(
    task_id: int,
    data: TaskCriteriaCreateRequestDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskCriteriaResponseDTO:
    data = TaskCriteriaCreateDTO(**data.model_dump(), task_id=task_id)
    return await task_criteria_service.create(data, user)


@router.post("/{task_id}/criteria/batch", response_model=SuccessOperationDTO)
async def create_criteria_batch_endpoint(
    task_id: int,
    data: TaskCriteriaCreateBatchDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await task_criteria_service.create_batch(task_id, data, user)
    return SuccessOperationDTO(message="Критерии прикреплены к задаче")


@router.get("/{task_id}/criteria", response_model=list[TaskCriteriaFullResponseDTO])
async def get_criteria_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> list[TaskCriteriaFullResponseDTO]:
    return await task_criteria_service.get_by_task(task_id, user)


@router.patch("/{task_id}/criteria/{task_criterion_id}", response_model=TaskCriteriaResponseDTO)
async def update_criterion_endpoint(
    task_criterion_id: int,
    data: TaskCriteriaUpdateWeightDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskCriteriaResponseDTO:
    return await task_criteria_service.update(task_criterion_id, data, user)


@router.delete("/{task_id}/criteria/{task_criterion_id}", response_model=SuccessOperationDTO)
async def delete_criterion_endpoint(
    task_criterion_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> SuccessOperationDTO:
    await task_criteria_service.delete(task_criterion_id, user)
    return SuccessOperationDTO(message="Критерий задачи удален")


@router.get("/{task_id}/solutions", response_model=list[SolutionShortResponseDTO])
async def get_list_by_task_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> list[SolutionShortResponseDTO]:
    return await solution_service.get_list_by_task(task_id, user)


@router.get("/{task_id}/available_criteria", response_model=list[CriterionResponseDTO])
async def get_available_criteria_endpoint(
    task_id: int,
user: Annotated[ShortUserDTO, Depends(get_current_user)],
    tags: Annotated[list[str] | None, Query()] =None,
    search: Annotated[str | None, Query()] =None,

) -> list[CriterionResponseDTO]:
    filters = CriterionFiltersDTO(
        tags=tags,
        search=search,
    )
    return await criteria_service.get_list_for_task(task_id, filters, user)


@router.post("/{task_id}/steps-models", response_model=TaskStepsModelDTO)
async def set_task_steps_model_endpoint(
    task_id: int,
    data: TaskStepsModelRequestCreateDTO,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskStepsModelDTO:
    return await set_task_steps_model(task_id, data, user)


@router.get("/{task_id}/steps-models", response_model=TaskStepsModelDTO)
async def get_task_steps_model_endpoint(
    task_id: int,
    user: Annotated[ShortUserDTO, Depends(get_current_user)],
) -> TaskStepsModelDTO:
    return await get_task_steps_model(task_id, user)
