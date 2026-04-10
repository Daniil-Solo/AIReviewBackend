import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.infrastructure.ai.llm import LLMInterface, Message


logger = logging.getLogger(__name__)


class DocImprover:
    def __init__(self, llm: LLMInterface) -> None:
        loader = FileSystemLoader(Path("src") / Path("prompts") / Path("project_doc"))
        env = Environment(loader=loader)
        self.system_prompt = env.get_template("improving/system.tpl")
        self.user_prompt = env.get_template("improving/user.tpl")
        self.llm = llm

    def run(self, project_doc: str, resolve_doc: str) -> str:
        messages = [
            Message(role="system", content=self.system_prompt.render()),
            Message(
                role="user",
                content=self.user_prompt.render(project_doc=project_doc, resolve_doc=resolve_doc),
            ),
        ]
        answer = self.llm.answer(messages, temperature=0.3)
        logger.warning(answer)
        return answer.content
