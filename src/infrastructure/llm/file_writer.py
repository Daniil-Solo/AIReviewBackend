import os
from pathlib import Path
from typing import Any

from src.infrastructure.llm.base import Answer, BaseLLM, Message


class FileWriterLLM(BaseLLM):
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def answer(self, messages: list[Message], **kwargs: Any) -> Answer:
        for idx, message in enumerate(messages):
            file_name = f"{idx + 1}_{message.role}.md"
            file_path = self.output_dir / file_name
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(message.content)
        return Answer(
            content="Used FileWriterLLM",
            in_tokens=None,
            out_tokens=None,
        )
