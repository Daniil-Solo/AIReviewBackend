from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface


class Jinja2PromptBuilder(PromptBuilderInterface):
    def __init__(self, prompts_dir_path: Path):
        self.env = Environment(
            loader=FileSystemLoader(prompts_dir_path),
            undefined=StrictUndefined
        )

    def build(self, prompt_path: str, **payload: Any) -> str:
        """
        - prompt_path - путь от директории со всеми промптами виду subdir/prompt.tpl
        - payload - словарь с данными, которые будут участвовать в рендеринге
        """
        template = self.env.get_template(prompt_path)
        return template.render(**payload)
