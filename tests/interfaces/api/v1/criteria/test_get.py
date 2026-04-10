from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.criteria.criteria import CriterionResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.criteria import create_criteria
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_get_criterion(client: AsyncClient):
    async def inner(criterion_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/criteria/{criterion_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_criterion(request_get_criterion):
    async def inner(criterion_id: int, token: str) -> CriterionResponseDTO:
        response = await request_get_criterion(criterion_id, token)
        assert response.status_code == status.HTTP_200_OK
        return CriterionResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__public_criterion(uow, get_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Public criterion", is_public=True))[0]

    result = await get_criterion(criterion.id, token)
    assert result.description == "Public criterion"
    assert result.is_public


async def test__success__private_criterion_by_creator(uow, get_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Private criterion", is_public=False))[0]

    result = await get_criterion(criterion.id, token)
    assert result.description == "Private criterion"


async def test__failed__private_criterion_by_other_user(uow, request_get_criterion):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Private criterion", is_public=False))[0]

    response = await request_get_criterion(criterion.id, other_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "criterion_access_denied"


async def test__failed__not_found(uow, request_get_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_criterion(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_get_criterion):
    response = await request_get_criterion(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
