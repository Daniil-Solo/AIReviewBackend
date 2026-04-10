import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.infrastructure.ai.llm import LLMInterface, Message
from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


logger = logging.getLogger(__name__)


class GapResolver:
    def __init__(self, llm: LLMInterface, processor: ProjectPreprocessor) -> None:
        loader = FileSystemLoader(Path("src") / Path("prompts") / Path("project_doc"))
        env = Environment(loader=loader)
        self.system_prompt = env.get_template("resolving/system.tpl")
        self.user_prompt = env.get_template("resolving/user.tpl")
        self.llm = llm
        self.processor = processor

    def run(self, project_doc: str, critic_docs: list[str]) -> str:
        messages = [
            Message(role="system", content=self.system_prompt.render()),
            Message(
                role="user",
                content=self.user_prompt.render(
                    project_tree=self.processor.get_tree(),
                    project_content=self.processor.get_content(),
                    project_doc=project_doc,
                    critic_docs=critic_docs,
                ),
            ),
        ]
        with open("file.md", "w", encoding="utf-8") as f:
            f.write(messages[0].content)
            f.write(messages[1].content)
        answer = self.llm.answer(messages, temperature=0.3)
        logger.warning(answer)
        return answer.content
