from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.custom_models import CustomModelRequestUpdateDTO
from src.dto.custom_models.custom_models import CustomModelDTO
from src.infrastructure.auth import create_access_token
from tests.factories.custom_models import CustomModelUpdateFactory
from tests.helpers.custom_models import create_custom_model
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_update_custom_model(client: AsyncClient):
    async def inner(model_id: int, data: CustomModelRequestUpdateDTO, token: str) -> Response:
        return await client.put(
            f"/api/v1/custom-models/{model_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_custom_model(request_update_custom_model):
    async def inner(model_id: int, data: CustomModelRequestUpdateDTO, token: str) -> CustomModelDTO:
        response = await request_update_custom_model(model_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return CustomModelDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, update_custom_model):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    model = await create_custom_model(uow, workspace.id, user.id)
    data: CustomModelRequestUpdateDTO = CustomModelUpdateFactory.build()

    updated = await update_custom_model(model.id, data, token)
    assert updated.name == data.name
    assert updated.model == data.model
    assert updated.base_url == data.base_url


async def test__failed__model_not_found(uow, request_update_custom_model):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    data: CustomModelRequestUpdateDTO = CustomModelUpdateFactory.build()

    response = await request_update_custom_model(9999, data, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "not_found"


async def test__failed__not_member(uow, request_update_custom_model):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    model = await create_custom_model(uow, workspace.id, user.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    data: CustomModelRequestUpdateDTO = CustomModelUpdateFactory.build()

    response = await request_update_custom_model(model.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_update_custom_model):
    data: CustomModelRequestUpdateDTO = CustomModelUpdateFactory.build()

    response = await request_update_custom_model(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
