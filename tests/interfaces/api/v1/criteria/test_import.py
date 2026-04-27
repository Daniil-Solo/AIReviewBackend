import io
import json

from fastapi import status
from httpx import AsyncClient, Response
from pydantic import TypeAdapter
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.criteria.criteria import CriterionResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.criteria import CriterionFactory
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import add_user_to_workspace, create_workspace


@pytest_asyncio.fixture()
def criteria_json_file():
    async def inner(criteria: list[dict] | None = None) -> tuple[bytes, str]:
        data = criteria or [
            {
                "description": "Test criterion 1",
                "prompt": "Check something 1",
                "tags": ["TAG1"],
                "stage": None,
            }
        ]
        return json.dumps(data).encode("utf-8"), "application/json"

    return inner


@pytest_asyncio.fixture()
def request_import_criteria(client: AsyncClient):
    async def inner(
        token: str,
        file_content: bytes,
        workspace_id: int | None = None,
        task_id: int | None = None,
    ) -> Response:
        files = {"file": ("criteria.json", io.BytesIO(file_content), "application/json")}
        data = {}
        if workspace_id is not None:
            data["workspace_id"] = str(workspace_id)
        if task_id is not None:
            data["task_id"] = str(task_id)

        return await client.post(
            "/api/v1/criteria/import",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def import_criteria(request_import_criteria):
    async def inner(
        token: str,
        file_content: bytes,
        workspace_id: int | None = None,
        task_id: int | None = None,
    ) -> list[CriterionResponseDTO]:
        response = await request_import_criteria(token, file_content, workspace_id, task_id)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[CriterionResponseDTO]).validate_json(response.text)

    return inner


async def test__success__public_criteria(uow, import_criteria, criteria_json_file):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    file_content, _ = await criteria_json_file()

    criteria = await import_criteria(token, file_content)

    assert len(criteria) == 1
    assert criteria[0].description == "Test criterion 1"
    assert criteria[0].workspace_id is None
    assert criteria[0].task_id is None
    assert criteria[0].created_by == user.id


async def test__success__workspace_criteria(uow, import_criteria, criteria_json_file):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)

    file_content, _ = await criteria_json_file()

    criteria = await import_criteria(token, file_content, workspace_id=workspace.id)

    assert len(criteria) == 1
    assert criteria[0].workspace_id == workspace.id


async def test__success__task_criteria(uow, import_criteria, criteria_json_file):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)

    file_content, _ = await criteria_json_file()

    criteria = await import_criteria(token, file_content, task_id=task.id)

    assert len(criteria) == 1
    assert criteria[0].task_id == task.id


async def test__success__bulk(uow, import_criteria):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    criteria_data = [
        {"description": "Criterion 1", "prompt": "Prompt 1", "tags": ["tag1"], "stage": None},
        {"description": "Criterion 2", "prompt": "Prompt 2", "tags": ["tag2"], "stage": None},
        {"description": "Criterion 3", "prompt": "Prompt 3", "tags": ["tag3"], "stage": None},
    ]
    file_content = json.dumps(criteria_data).encode("utf-8")

    criteria = await import_criteria(token, file_content)

    assert len(criteria) == 3
    assert criteria[0].description == "Criterion 1"
    assert criteria[1].description == "Criterion 2"
    assert criteria[2].description == "Criterion 3"


async def test__success__tags_normalized(uow, import_criteria, criteria_json_file):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    file_content, _ = await criteria_json_file(
        [{"description": "Test", "prompt": "Prompt", "tags": ["UPPERCASE", "MixedCase"], "stage": None}]
    )

    criteria = await import_criteria(token, file_content)

    assert len(criteria) == 1
    assert "uppercase" in criteria[0].tags
    assert "mixedcase" in criteria[0].tags


async def test__success__empty_json(uow, import_criteria):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    file_content = b"[]"

    criteria = await import_criteria(token, file_content)

    assert criteria == []


async def test__failed__invalid_json(uow, request_import_criteria):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    file_content = b"[{}]"

    response = await request_import_criteria(token, file_content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    assert response.json()["code"] == "invalid_file_format"


async def test__failed__unauthorized(request_import_criteria, criteria_json_file):
    file_content, _ = await criteria_json_file()

    response = await request_import_criteria(token="invalid", file_content=file_content)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test__failed__student_cannot_import_workspace(uow, request_import_criteria, criteria_json_file):
    user = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, user.id)
    await add_user_to_workspace(uow, workspace.id, student.id, role=WorkspaceMemberRoleEnum.STUDENT)

    file_content, _ = await criteria_json_file()

    response = await request_import_criteria(token, file_content, workspace_id=workspace.id)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__non_admin_cannot_import_public(uow, request_import_criteria, criteria_json_file):
    user = (await create_users(uow, is_admin=False))[0]
    token = create_access_token(user.as_short())

    file_content, _ = await criteria_json_file()

    response = await request_import_criteria(token, file_content)
    assert response.status_code == status.HTTP_403_FORBIDDEN
