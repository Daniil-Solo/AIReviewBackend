from pathlib import Path

import click
from rich.console import Console

from src.services.project.preprocessing.preprocessing import ProjectPreprocessor


console = Console()


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def main(directory: Path) -> None:
    project_processor = ProjectPreprocessor(project_path=Path(directory))

    info = project_processor.get_info()

    console.print(f"[bold green]Количество файлов: {info.files_count} [/bold green]")
    console.print(f"[bold green]Количество символов: {info.chars_count} [/bold green]")
    console.print(f"[bold green]Количество токенов: {info.tokens_count} [/bold green]")


if __name__ == "__main__":
    main()
