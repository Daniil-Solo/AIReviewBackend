from src.constants.transactions import TransactionTypeEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.transactions.metadata import LLMCallTransactionMetadataDTO
from src.dto.transactions.transactions import (
    TransactionCreateDTO,
)
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings


logger = get_logger()


async def charge_for_llm_call(uow: UnitOfWork, workspace_id: int, metadata: LLMCallTransactionMetadataDTO) -> None:
    workspace = await uow.workspaces.get_by_id(workspace_id)
    owner_member = (
        await uow.workspace_members.get_list(
            WorkspaceMemberFiltersDTO(workspace_id=workspace.id, roles=[WorkspaceMemberRoleEnum.OWNER])
        )
    )[0]
    input_cost = metadata.input_tokens * settings.ai.LLM_DEFAULT_MODEL_INPUT_TOKEN_PRICE / 1_000_000
    output_cost = metadata.output_tokens * settings.ai.LLM_DEFAULT_MODEL_OUTPUT_TOKEN_PRICE / 1_000_000
    total_cost = input_cost + output_cost

    data = TransactionCreateDTO(
        user_id=owner_member.user_id,
        amount=-total_cost,
        type=TransactionTypeEnum.LLM_CALL,
        metadata=metadata.model_dump(),
    )
    await uow.transactions.create(data)
