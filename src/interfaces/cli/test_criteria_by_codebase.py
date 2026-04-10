import time

import asyncclick as click
from rich.console import Console

from src.application.ai_review.criteria_grading import grade_by_codebase
from src.di.container import init_container, shutdown_container


console = Console()


@click.command()
async def main() -> None:
    container = await init_container()
    start = time.perf_counter()
    try:
        await grade_by_codebase()
        console.print("[bold green]Выполнено [/bold green]")
    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}[/bold red]")
    finally:
        delta = time.perf_counter() - start
        console.print(f"[bold yellow]Время выполнения: {delta:.0f} с. [/bold yellow]")
        await shutdown_container(container)


if __name__ == "__main__":
    main()
