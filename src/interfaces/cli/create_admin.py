import asyncclick as click
from rich.console import Console

from src.application.users.users import create_admin
from src.di.container import init_container, shutdown_container
from src.dto.users.user import UserCreateDTO


console = Console()


@click.command()
@click.option("--email", prompt=True, help="Email администратора")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Пароль")
@click.option("--fullname", prompt=True, help="Полное имя")
async def main(email: str, password: str, fullname: str) -> None:
    container = await init_container()
    try:
        data = UserCreateDTO(email=email, password=password, fullname=fullname)
        user = await create_admin(data)
        console.print(f"[bold green]Администратор {user.email} успешно создан![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}[/bold red]")
    finally:
        await shutdown_container(container)


if __name__ == "__main__":
    main()
