from fastapi import APIRouter, Depends
from fastapi.params import Query

from src.application.workspaces import (
    archive_workspace,
    change_workspace_owner,
    check_slug_available,
    create_join_rule,
    create_workspace,
    delete_join_rule,
    get_workspace,
    get_workspace_join_rules,
    get_workspace_members,
    get_workspace_tasks,
    leave_workspace,
    update_join_rule,
    update_member,
    update_workspace,
)
from src.dto.common import SuccessOperationDTO
from src.dto.tasks.tasks import TaskResponseDTO
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces import (
    SlugCheckResponseDTO,
    TransferOwnershipDTO,
    WorkspaceCreateDTO,
    WorkspaceMemberResponseDTO,
    WorkspaceMemberUpdateDTO,
    WorkspaceResponseDTO,
    WorkspaceUpdateDTO,
)
from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleRequestCreateDTO,
    WorkspaceJoinRuleRequestUpdateDTO,
    WorkspaceJoinRuleResponseDTO,
)
from src.interfaces.api.dependencies import get_current_user


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponseDTO)
async def create_workspace_endpoint(
    data: WorkspaceCreateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceResponseDTO:
    return await create_workspace(data, user)


@router.put("/{workspace_id}", response_model=WorkspaceResponseDTO)
async def update_workspace_endpoint(
    workspace_id: int,
    data: WorkspaceUpdateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceResponseDTO:
    return await update_workspace(workspace_id, data, user)


@router.delete("/{workspace_id}")
async def archive_workspace_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await archive_workspace(workspace_id, user)
    return SuccessOperationDTO(message="Пространство архивировано")


@router.get("/{workspace_id}", response_model=WorkspaceResponseDTO)
async def get_workspace_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceResponseDTO:
    return await get_workspace(workspace_id, user)


@router.get("/{workspace_id}/tasks", response_model=list[TaskResponseDTO])
async def get_workspace_tasks_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> list[TaskResponseDTO]:
    return await get_workspace_tasks(workspace_id, user)


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponseDTO])
async def get_workspace_members_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> list[WorkspaceMemberResponseDTO]:
    return await get_workspace_members(workspace_id, user)


@router.get("/{workspace_id}/join_rules", response_model=list[WorkspaceJoinRuleResponseDTO])
async def get_workspace_join_rules_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> list[WorkspaceJoinRuleResponseDTO]:
    return await get_workspace_join_rules(workspace_id, user)


@router.post("/{workspace_id}/join_rules", response_model=WorkspaceJoinRuleResponseDTO)
async def create_join_rule_endpoint(
    workspace_id: int,
    data: WorkspaceJoinRuleRequestCreateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceJoinRuleResponseDTO:
    return await create_join_rule(workspace_id, data, user)


@router.put("/{workspace_id}/join_rules/{rule_id}", response_model=WorkspaceJoinRuleResponseDTO)
async def update_join_rule_endpoint(
    workspace_id: int,
    rule_id: int,
    data: WorkspaceJoinRuleRequestUpdateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceJoinRuleResponseDTO:
    return await update_join_rule(workspace_id, rule_id, data, user)


@router.delete("/{workspace_id}/join_rules/{rule_id}", response_model=SuccessOperationDTO)
async def delete_join_rule_endpoint(
    workspace_id: int,
    rule_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await delete_join_rule(workspace_id, rule_id, user)
    return SuccessOperationDTO(message="Правило приглашения удалено")


@router.patch("/{workspace_id}/members/{member_id}", response_model=WorkspaceMemberResponseDTO)
async def update_member_endpoint(
    workspace_id: int,
    member_id: int,
    data: WorkspaceMemberUpdateDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceMemberResponseDTO:
    return await update_member(workspace_id, member_id, data, user)


@router.post("/{workspace_id}/leave", response_model=SuccessOperationDTO)
async def leave_workspace_endpoint(
    workspace_id: int,
    user: ShortUserDTO = Depends(get_current_user),
) -> SuccessOperationDTO:
    await leave_workspace(workspace_id, user)
    return SuccessOperationDTO(message="Пользователь покинул пространство")


@router.patch("/{workspace_id}/owner", response_model=WorkspaceResponseDTO)
async def transfer_ownership_endpoint(
    workspace_id: int,
    data: TransferOwnershipDTO,
    user: ShortUserDTO = Depends(get_current_user),
) -> WorkspaceResponseDTO:
    return await change_workspace_owner(workspace_id, data, user)


@router.post("/slugs/availability", response_model=SlugCheckResponseDTO)
async def check_slug_endpoint(
    slug: str = Query(),
) -> SlugCheckResponseDTO:
    return await check_slug_available(slug)
