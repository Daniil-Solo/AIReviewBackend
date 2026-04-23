from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.criteria.criteria import CriterionCreateDTO, CriterionResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.criteria import CriterionFactory
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_create_criterion(client: AsyncClient):
    async def inner(data: CriterionCreateDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/criteria",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_criterion(request_create_criterion):
    async def inner(data: CriterionCreateDTO, token: str) -> CriterionResponseDTO:
        response = await request_create_criterion(data, token)
        assert response.status_code == status.HTTP_200_OK
        return CriterionResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, create_criterion):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())
    data: CriterionCreateDTO = CriterionFactory.build()

    criterion = await create_criterion(data, token)
    assert criterion.description == data.description
    assert criterion.tags == data.tags
    assert criterion.created_by == user.id


async def test__failed__unauthorized(request_create_criterion):
    data: CriterionCreateDTO = CriterionFactory.build()

    response = await request_create_criterion(data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
