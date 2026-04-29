from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.custom_models import CustomModelRequestCreateDTO
from src.dto.custom_models.custom_models import CustomModelDTO
from src.infrastructure.auth import create_access_token
from tests.factories.custom_models import CustomModelFactory
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_create_custom_model(client: AsyncClient):
    async def inner(workspace_id: int, data: CustomModelRequestCreateDTO, token: str) -> Response:
        return await client.post(
            f"/api/v1/workspaces/{workspace_id}/custom-models",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_custom_model_endpoint(request_create_custom_model):
    async def inner(workspace_id: int, data: CustomModelRequestCreateDTO, token: str) -> CustomModelDTO:
        response = await request_create_custom_model(workspace_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return CustomModelDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, create_custom_model_endpoint):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    data: CustomModelRequestCreateDTO = CustomModelFactory.build()

    model = await create_custom_model_endpoint(workspace.id, data, token)
    assert model.name == data.name
    assert model.model == data.model
    assert model.base_url == data.base_url
    assert model.workspace_id == workspace.id


async def test__failed__workspace_not_found(uow, request_create_custom_model):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    data: CustomModelRequestCreateDTO = CustomModelFactory.build()

    response = await request_create_custom_model(9999, data, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "not_found"


async def test__failed__not_member(uow, request_create_custom_model):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    data: CustomModelRequestCreateDTO = CustomModelFactory.build()

    response = await request_create_custom_model(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_create_custom_model):
    data: CustomModelRequestCreateDTO = CustomModelFactory.build()

    response = await request_create_custom_model(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
