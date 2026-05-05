from dependency_injector.wiring import Provide, inject

from src.application.exceptions import EntityNotFoundError
from src.constants.ai_pipeline import PipelineStepEnum
from src.di.container import Container
from src.dto.transactions.metadata import LLMCallTransactionMetadataDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.llm.openai_like import OpenAILikeLLM
from src.infrastructure.encryptor.interface import BaseEncryptor
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def get_llm_for_step(
    uow: UnitOfWork,
    solution_id: int,
    step: PipelineStepEnum,
    default_model: LLMInterface = Provide[Container.default_model],
    encryptor: BaseEncryptor = Provide[Container.encryptor],
) -> tuple[LLMInterface, LLMCallTransactionMetadataDTO]:
    solution = await uow.solutions.get_by_id(solution_id)
    task = await uow.tasks.get_by_id(solution.task_id)
    try:
        task_steps_model = await uow.task_steps_models.get(task.id)
    except EntityNotFoundError:
        return default_model, LLMCallTransactionMetadataDTO(
            solution_id=solution_id,
            task=step,
            model="default",
        )

    model_id = task_steps_model.steps.get(step)

    if model_id is None:
        return default_model, LLMCallTransactionMetadataDTO(
            solution_id=solution_id,
            task=step,
            model="default",
        )

    custom_model = await uow.custom_models.get_by_id(model_id)
    api_key = encryptor.decrypt(custom_model.encrypted_api_key)

    custom_llm = OpenAILikeLLM(
        base_url=custom_model.base_url,
        api_key=api_key,
        model=custom_model.model,
        common_parameters={"stream": False, "temperature": 0.1},
    )

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id,
        task=step,
        model="custom:" + custom_model.name,
    )

    return custom_llm, metadata
