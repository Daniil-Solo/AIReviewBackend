from pathlib import Path
import string

import click
from rich.console import Console

from src.infrastructure.ai.llm import OpenAILikeLLM
from src.services.project.document_generation.creating import DocumentCreator
from src.services.project.document_generation.cricitc import Critic
from src.services.project.document_generation.improving import DocImprover
from src.services.project.document_generation.resolving import GapResolver
from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


console = Console()


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), default="final_project_doc.md", help="Имя выходного файла")
def main(directory: Path, output: Path) -> None:
    llm_1 = OpenAILikeLLM(base_url, api_key, model_1)
    model_2 = "minimax/minimax-m2.5"
    llm_2 = OpenAILikeLLM(base_url, api_key, model_2)
    model_3 = "z-ai/glm-4.7-flash"
    llm_3 = OpenAILikeLLM(base_url, api_key, model_3)

    console.print("[bold green]Стартуем[/bold green]")
    project_processor = ProjectPreprocessor(project_path=Path(directory))

    creator = DocumentCreator(llm_1, project_processor)
    project_doc = creator.generate()
    with open("project_doc.md", "w", encoding="utf-8") as f:
        f.write(project_doc)
    console.print("[bold green]Первичный ProjectDoc сформирован[/bold green]")

    critic_docs = []
    for idx, llm in enumerate([llm_1, llm_2, llm_3]):
        critic = Critic(llm)
        critic_doc = critic.run(project_doc, string.ascii_letters[idx].upper())
        with open(f"critic_doc_{idx + 1}.md", "w", encoding="utf-8") as f:
            f.write(critic_doc)
        console.print(f"[bold green]Критика {idx + 1} ProjectDoc составлена[/bold green]")
        critic_docs.append(critic_doc)

    resolver = GapResolver(llm_1, project_processor)
    resolve_doc = resolver.run(project_doc, critic_docs)
    with open("resolve_doc.md", "w", encoding="utf-8") as f:
        f.write(resolve_doc)
    console.print("[bold green]Рекомендации по улучшению ProjectDoc получены[/bold green]")

    improver = DocImprover(llm_1)
    final_project_doc = improver.run(project_doc, resolve_doc)
    with open(output, "w", encoding="utf-8") as f:
        f.write(final_project_doc)
    console.print("[bold green]ProjectDoc финализирован[/bold green]")

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
