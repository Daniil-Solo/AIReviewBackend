from typing import Any

from openai import AsyncOpenAI

from src.dto.ai_review.message import AIAnswerDTO, InputMessageDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class OpenAILikeLLM(LLMInterface):
    def __init__(self, base_url: str, api_key: str, model: str, common_parameters: dict[str, Any]) -> None:
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.common_parameters = common_parameters

    async def answer(self, messages: list[InputMessageDTO], **kwargs: Any) -> AIAnswerDTO:
        response = await self.client.chat.completions.create(
            model=self.model, messages=[msg.model_dump() for msg in messages], **self.common_parameters, **kwargs
        )
        answer = AIAnswerDTO(
            content=response.choices[0].message.content or "",
            in_tokens=response.usage.prompt_tokens if response.usage is not None else None,
            out_tokens=response.usage.completion_tokens if response.usage is not None else None,
        )
        logger.info(
            "llm_response_received",
            model=self.model,
            content_legth=len(answer.content) if answer.content is not None else 0,
            in_tokens=response.usage.prompt_tokens if response.usage else None,
            out_tokens=response.usage.completion_tokens if response.usage else None,
        )
        return answer

    async def run(self, system_text: str, user_text: str, **kwargs: Any) -> AIAnswerDTO:
        messages = [
            InputMessageDTO(role="system", content=system_text),
            InputMessageDTO(role="user", content=user_text),
        ]
        return await self.answer(messages, **kwargs)
