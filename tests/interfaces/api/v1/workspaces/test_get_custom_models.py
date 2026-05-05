from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio
from pydantic import TypeAdapter

from src.dto.custom_models.custom_models import CustomModelDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.custom_models import create_custom_model
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_custom_models(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/custom-models",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_custom_models(request_get_custom_models):
    async def inner(workspace_id: int, token: str) -> list[CustomModelDTO]:
        response = await request_get_custom_models(workspace_id, token)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[CustomModelDTO]).validate_json(response.text)

    return inner


async def test__success(uow, get_custom_models):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    await create_custom_model(uow, workspace.id, user.id, name="model-1")
    await create_custom_model(uow, workspace.id, user.id, name="model-2")

    models = await get_custom_models(workspace.id, token)
    assert len(models) == 2


async def test__success__empty_list(uow, request_get_custom_models):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_get_custom_models(workspace.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test__failed__workspace_not_found(uow, request_get_custom_models):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_custom_models(9999, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__not_member(uow, request_get_custom_models):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    response = await request_get_custom_models(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_get_custom_models):
    response = await request_get_custom_models(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
