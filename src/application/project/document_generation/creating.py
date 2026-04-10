import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.infrastructure.ai.llm import LLMInterface, Message
from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


logger = logging.getLogger(__name__)


class DocumentCreator:
    def __init__(self, llm: LLMInterface, processor: ProjectPreprocessor) -> None:
        loader = FileSystemLoader(Path("src") / Path("prompts") / Path("project_doc"))
        env = Environment(loader=loader)
        self.system_prompt = env.get_template("creating/system.tpl")
        self.user_prompt = env.get_template("creating/user.tpl")
        self.llm = llm
        self.processor = processor

    def generate(self) -> str:
        messages = [
            Message(role="system", content=self.system_prompt.render()),
            Message(
                role="user",
                content=self.user_prompt.render(
                    project_tree=self.processor.get_tree(), project_content=self.processor.get_content()
                ),
            ),
        ]
        answer = self.llm.answer(messages, temperature=0.3)
        logger.warning(answer)
        return answer.content
