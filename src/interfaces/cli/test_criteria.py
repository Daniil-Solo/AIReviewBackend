import time

import asyncclick as click
from rich.console import Console

from src.application.ai_review.criteria_grading import grade_by_project_doc
from src.di.container import init_container, shutdown_container


console = Console()


@click.command()
async def main() -> None:
    container = await init_container()
    try:
        start = time.perf_counter()
        await grade_by_project_doc()
        delta = time.perf_counter() - start
        console.print(f"[bold green]Выполнено за {delta:.0f} с. [/bold green]")
    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}[/bold red]")
    finally:
        await shutdown_container(container)


if __name__ == "__main__":
    main()
