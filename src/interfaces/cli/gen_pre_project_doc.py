from pathlib import Path

import click
from rich.console import Console

from src.infrastructure.llm.openai_like import OpenAILikeLLM
from src.services.project.document_generation.creating import DocumentGenerator
from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


console = Console()


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), default="project_doc.md", help="Имя выходного файла")
def main(directory: Path, output: Path) -> None:
    model = "openrouter/hunter-alpha"

    llm = OpenAILikeLLM(base_url, api_key, model)
    project_processor = ProjectPreprocessor(project_path=Path(directory))

    generator = DocumentGenerator(llm, project_processor)
    report_text = generator.generate()
    with open(output, "w", encoding="utf-8") as f:
        f.write(report_text)

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
