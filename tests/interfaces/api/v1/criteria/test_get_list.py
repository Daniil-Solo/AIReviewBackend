from fastapi import status
from httpx import AsyncClient, Response
from pydantic import TypeAdapter
import pytest_asyncio

from src.dto.criteria.criteria import CriterionResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.criteria import create_criteria
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_list_criteria(client: AsyncClient):
    async def inner(token: str, **kwargs) -> Response:
        params = {k: v for k, v in kwargs.items() if v is not None}
        return await client.get(
            "/api/v1/criteria",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_list_criteria(request_list_criteria):
    async def inner(token: str, **kwargs) -> list[CriterionResponseDTO]:
        response = await request_list_criteria(token, **kwargs)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[CriterionResponseDTO]).validate_json(response.text)

    return inner


async def test__success__public_criteria(uow, get_list_criteria):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    await create_criteria(uow, user.id, is_public=True, size=2)

    criteria = await get_list_criteria(token)
    assert len(criteria) == 2


async def test__success__private_criteria_visible_only_to_creator(uow, get_list_criteria):
    user, other_user = await create_users(uow, size=2)
    token = create_access_token(user.as_short())
    other_token = create_access_token(other_user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Private criterion", is_public=False))[0]

    user_criteria = await get_list_criteria(token)
    assert len(user_criteria) == 1
    assert user_criteria[0].description == criterion.description

    other_criteria = await get_list_criteria(other_token)
    assert len(other_criteria) == 0


async def test__success__filter_by_tags(uow, get_list_criteria):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    await create_criteria(uow, user.id, description="Criterion with tag", tags=["python"], is_public=True)

    criteria = await get_list_criteria(token, tags=["python"])
    assert len(criteria) == 1
    assert "python" in criteria[0].tags


async def test__success__filter_by_search_query(uow, get_list_criteria):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    await create_criteria(uow, user.id, description="This is a Python test criterion", is_public=True)
    await create_criteria(uow, user.id, is_public=True)

    criteria = await get_list_criteria(token, search="Python")
    assert len(criteria) == 1
    assert "Python" in criteria[0].description


async def test__failed__unauthorized(request_list_criteria):
    response = await request_list_criteria(token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
