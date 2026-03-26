from pathlib import Path

import click
from rich.console import Console

from src.infrastructure.llm.openai_like import OpenAILikeLLM
from src.services.project.document_generation.resolving import GapResolver
from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


console = Console()


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument("project_doc_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("critic_doc_1_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("critic_doc_2_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("critic_doc_3_file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(), default="resolve_doc.md", help="Имя выходного файла")
def main(
    directory: Path,
    project_doc_file: Path,
    critic_doc_1_file: Path,
    critic_doc_2_file: Path,
    critic_doc_3_file: Path,
    output: Path,
) -> None:
    model = "qwen/qwen3-235b-a22b-2507"

    llm = OpenAILikeLLM(base_url, api_key, model)
    project_processor = ProjectPreprocessor(project_path=Path(directory))

    with open(project_doc_file, encoding="utf-8") as f:
        project_doc = f.read()

    critic_docs = []
    for critic_doc_file in [critic_doc_1_file, critic_doc_2_file, critic_doc_3_file]:
        with open(critic_doc_file, encoding="utf-8") as f:
            critic_doc = f.read()
        critic_docs.append(critic_doc)

    generator = GapResolver(llm, project_processor)
    report_text = generator.run(project_doc, critic_docs)

    with open(output, "w", encoding="utf-8") as f:
        f.write(report_text)

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
