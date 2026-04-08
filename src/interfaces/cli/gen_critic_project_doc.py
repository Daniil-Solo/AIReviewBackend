from pathlib import Path

import click
from rich.console import Console

from src.infrastructure.ai.llm import OpenAILikeLLM
from src.services.project.document_generation.cricitc import Critic


console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(), default="critic_project_doc.md", help="Имя выходного файла")
def main(input_file: Path, output: Path) -> None:
    model = "z-ai/glm-4.7"
    #
    llm = OpenAILikeLLM(base_url, api_key, model)
    critic = Critic(llm)

    with open(input_file, encoding="utf-8") as f:
        project_doc = f.read()

    report_text = critic.run(project_doc, letter_prefix="E")

    with open(output, "w", encoding="utf-8") as f:
        f.write(report_text)

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
