from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.dto.workspaces.workspace import WorkspaceCreateDTO, WorkspaceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.workspaces import WorkspaceFactory
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_create_workspace(client: AsyncClient):
    async def inner(data: WorkspaceCreateDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/workspaces",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_workspace(request_create_workspace):
    async def inner(data: WorkspaceCreateDTO, token: str) -> WorkspaceResponseDTO:
        response = await request_create_workspace(data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, create_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    data: WorkspaceCreateDTO = WorkspaceFactory.build()

    workspace = await create_workspace(data, token)
    assert workspace.name == data.name
    assert workspace.description == data.description
    assert not workspace.is_archived

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        assert len(members) == 1
        assert members[0].user_id == user.id


async def test__failed__unauthorized(request_create_workspace):
    data: WorkspaceCreateDTO = WorkspaceFactory.build()

    response = await request_create_workspace(data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
