from pathlib import Path

import click
from rich.console import Console

from src.infrastructure.ai.llm import OpenAILikeLLM
from src.services.project.document_generation.improving import DocImprover


console = Console()


@click.command()
@click.argument("project_doc_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("resolve_doc_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(), default="final_project_doc.md", help="Имя выходного файла")
def main(project_doc_file: Path, resolve_doc_file: Path, output: Path) -> None:
    model = "moonshotai/kimi-k2.5"

    llm = OpenAILikeLLM(base_url, api_key, model)
    improver = DocImprover(llm)

    with open(project_doc_file, encoding="utf-8") as f:
        project_doc = f.read()

    with open(resolve_doc_file, encoding="utf-8") as f:
        resolve_doc = f.read()

    report_text = improver.run(project_doc, resolve_doc)

    with open(output, "w", encoding="utf-8") as f:
        f.write(report_text)

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
