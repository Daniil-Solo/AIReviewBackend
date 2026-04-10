from pathlib import Path

import click
from rich.console import Console

from src.application.project.preprocessing.preprocessing import ProjectPreprocessor


console = Console()


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), default="project_tree.md", help="Имя выходного файла")
def main(directory: Path, output: Path) -> None:
    project_processor = ProjectPreprocessor(project_path=Path(directory))

    tree_text = project_processor.get_tree()
    with open(output, "w", encoding="utf-8") as f:
        f.write(tree_text)

    console.print(f"[bold green]Сгенерирован файл: {output} [/bold green]")


if __name__ == "__main__":
    main()
