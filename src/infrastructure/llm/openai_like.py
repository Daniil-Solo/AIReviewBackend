from typing import Any

from openai import OpenAI

from src.infrastructure.llm.base import Answer, BaseLLM, Message
from src.infrastructure.logging import get_logger


logger = get_logger()


class OpenAILikeLLM(BaseLLM):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def answer(self, messages: list[Message], **kwargs: Any) -> Answer:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[msg.__dict__ for msg in messages],
            max_tokens=16384,
            stream=False,
            temperature=0,
            **kwargs,
        )
        logger.info(
            "llm_response_received",
            model=self.model,
            in_tokens=response.usage.prompt_tokens if response.usage else None,
            out_tokens=response.usage.completion_tokens if response.usage else None,
        )
        if response.choices is None:
            raise RuntimeError(response)

        return Answer(
            content=response.choices[0].message.content or "",
            in_tokens=response.usage.prompt_tokens if response.usage is not None else None,
            out_tokens=response.usage.completion_tokens if response.usage is not None else None,
        )
