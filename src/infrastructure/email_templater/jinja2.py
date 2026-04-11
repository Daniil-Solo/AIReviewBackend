from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from src.infrastructure.email_templater.interface import EmailTemplaterInterface


class Jinja2EmailTemplater(EmailTemplaterInterface):
    def __init__(self, templates_dir_path: Path):
        self.env = Environment(loader=FileSystemLoader(templates_dir_path), undefined=StrictUndefined)

    def render(self, template: str, **kwargs: Any) -> tuple[str, str, str]:
        subject_template = self.env.get_template(f"{template}/subject.txt")
        subject = subject_template.render(**kwargs)
        plain_template = self.env.get_template(f"{template}/template.txt")
        plain = plain_template.render(**kwargs)
        html_template = self.env.get_template(f"{template}/template.html")
        html = html_template.render(**kwargs)
        return subject, plain, html
