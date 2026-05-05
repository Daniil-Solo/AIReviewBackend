from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.criteria.criteria import CriterionResponseDTO, CriterionUpdateDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.criteria import create_criteria
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_update_criterion(client: AsyncClient):
    async def inner(criterion_id: int, data: CriterionUpdateDTO, token: str) -> Response:
        return await client.put(
            f"/api/v1/criteria/{criterion_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_criterion(request_update_criterion):
    async def inner(criterion_id: int, data: CriterionUpdateDTO, token: str) -> CriterionResponseDTO:
        response = await request_update_criterion(criterion_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return CriterionResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, update_criterion):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Original description"))[0]

    data = CriterionUpdateDTO(description="Updated description", tags=["new_tag"], prompt="Updated prompt")
    result = await update_criterion(criterion.id, data, token)

    assert result.description == "Updated description"
    assert "new_tag" in result.tags
    assert result.prompt == "Updated prompt"
    assert result.is_public


async def test__failed__not_creator(uow, request_update_criterion):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    criterion = (await create_criteria(uow, user.id, description="Original description"))[0]

    data = CriterionUpdateDTO(description="Updated description", prompt="Updated prompt")
    response = await request_update_criterion(criterion.id, data, other_token)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "criterion_access_denied"


async def test__failed__not_found(uow, request_update_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    data = CriterionUpdateDTO(description="Updated description", prompt="Updated prompt")
    response = await request_update_criterion(9999, data, token)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_update_criterion):
    data = CriterionUpdateDTO(description="Updated description", prompt="Updated prompt")

    response = await request_update_criterion(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
