import datetime

from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError, EntityNotFoundError
from src.application.workspaces.common import check_member_role
from src.constants.ai_pipeline import LLM_STEPS
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.custom_models import (
    CustomModelDTO,
    CustomModelFiltersDTO,
    CustomModelRequestCreateDTO,
    CustomModelRequestUpdateDTO,
    TaskStepsModelDTO,
    TaskStepsModelRequestCreateDTO,
)
from src.dto.custom_models.custom_models import (
    CustomModelCreateDTO,
    CustomModelUpdateDTO,
    CustomModelWithAPIKeyDTO,
    TaskStepsModelUpsertDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.ai.llm.openai_like import OpenAILikeLLM
from src.infrastructure.encryptor.interface import BaseEncryptor
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = get_logger()


async def validate_custom_model(base_url: str, api_key: str, model: str) -> None:
    try:
        llm = OpenAILikeLLM(
            base_url=base_url,
            api_key=api_key,
            model=model,
            common_parameters={"stream": False, "temperature": 0.1},
        )
        test_result = await llm.run("You are a helpful assistant.", "Say 'OK' if you can understand this.")
        if not test_result.content:
            raise ApplicationError(message="Не удалось получить ответ от LLM", code="llm_validation_failed")
    except Exception as e:
        logger.error("LLM validation failed", error=str(e))
        raise ApplicationError(
            message=f"Не удалось подключиться к LLM API.\n Ошибка: {str(e)}", code="llm_validation_failed"
        ) from e


@inject
async def create_custom_model(
    data: CustomModelRequestCreateDTO,
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    encryptor: BaseEncryptor = Provide[Container.encryptor],
) -> CustomModelDTO:
    await validate_custom_model(data.base_url, data.api_key, data.model)

    create_data = CustomModelCreateDTO(
        name=data.name,
        model=data.model,
        base_url=data.base_url,
        encrypted_api_key=encryptor.encrypt(data.api_key),
        workspace_id=workspace_id,
    )

    async with uow.connection():
        workspace = await uow.workspaces.get_by_id(workspace_id)
        await check_member_role(
            uow, user.id, workspace.id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        return await uow.custom_models.create(create_data, user.id)


@inject
async def update_custom_model(
    model_id: int,
    data: CustomModelRequestUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    encryptor: BaseEncryptor = Provide[Container.encryptor],
) -> CustomModelDTO:
    await validate_custom_model(data.base_url, data.api_key, data.model)

    update_data = CustomModelUpdateDTO(
        name=data.name,
        model=data.model,
        base_url=data.base_url,
        encrypted_api_key=encryptor.encrypt(data.api_key),
    )

    async with uow.connection():
        model = await uow.custom_models.get_by_id(model_id)
        await check_member_role(
            uow, user.id, model.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        return await uow.custom_models.update(model_id, update_data)


@inject
async def delete_custom_model(
    model_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        model = await uow.custom_models.get_by_id(model_id)
        await check_member_role(
            uow, user.id, model.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        await uow.custom_models.delete(model_id)
        await uow.task_steps_models.clear_model_references(model.workspace_id, model_id)


@inject
async def get_workspace_custom_models(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CustomModelDTO]:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        return await uow.custom_models.get_list(CustomModelFiltersDTO(workspace_id=workspace_id))


@inject
async def get_custom_model(
    model_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    encryptor: BaseEncryptor = Provide[Container.encryptor],
) -> CustomModelWithAPIKeyDTO:
    async with uow.connection():
        model = await uow.custom_models.get_by_id(model_id)
        await check_member_role(
            uow, user.id, model.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
    return CustomModelWithAPIKeyDTO(**dict(**model.model_dump(), api_key=encryptor.decrypt(model.encrypted_api_key)))


@inject
async def set_task_steps_model(
    task_id: int,
    data: TaskStepsModelRequestCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskStepsModelDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow, user.id, task.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        upsert_data = TaskStepsModelUpsertDTO(task_id=task_id, steps=data.steps)
        return await uow.task_steps_models.upsert(upsert_data)


@inject
async def get_task_steps_model(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskStepsModelDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow, user.id, task.workspace_id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        try:
            return await uow.task_steps_models.get(task_id)
        except EntityNotFoundError:
            return TaskStepsModelDTO(
                task_id=task_id,
                steps=dict.fromkeys(LLM_STEPS),
                created_at=datetime.datetime.now(tz=datetime.UTC),
            )
