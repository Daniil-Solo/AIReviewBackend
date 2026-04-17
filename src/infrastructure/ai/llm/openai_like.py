from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.util import await_only

from src.dto.ai_review.message import AIAnswerDTO, InputMessageDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class OpenAILikeLLM(LLMInterface):
    def __init__(self, base_url: str, api_key: str, model: str, common_parameters: dict[str, Any]) -> None:
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.common_parameters = common_parameters

    async def answer(self, messages: list[InputMessageDTO], retry: int = 1, **kwargs: Any) -> AIAnswerDTO:
        response = await self.client.chat.completions.create(
            model=self.model, messages=[msg.model_dump() for msg in messages], **self.common_parameters, **kwargs
        )
        answer = AIAnswerDTO(
            content=response.choices[0].message.content or "",
            input_tokens=response.usage.prompt_tokens if response.usage is not None else 0,
            output_tokens=response.usage.completion_tokens if response.usage is not None else 0,
        )
        logger.info(
            "llm_response_received",
            model=self.model,
            input_tokens=answer.input_tokens,
            output_tokens=answer.output_tokens,
        )
        # Баг на стороне провайдера, ответ обрубается в 4096 токенов
        if answer.output_tokens == 4096:
            logger.info("llm_calling_retry", retry=retry)
            if retry < 3:
                return await self.answer(messages, retry=retry+1, **kwargs)

        return answer

    async def run(self, system_text: str, user_text: str, **kwargs: Any) -> AIAnswerDTO:
        messages = [
            InputMessageDTO(role="system", content=system_text),
            InputMessageDTO(role="user", content=user_text),
        ]
        return await self.answer(messages, **kwargs)
