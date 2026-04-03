import asyncclick as click
from rich.console import Console

from src.application.users import users as users_service
from src.dto.users.user import UserCreateDTO
from src.infrastructure.di.container import init_container


console = Console()


@click.command()
@click.option("--email", prompt=True, help="Email администратора")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Пароль")
@click.option("--fullname", prompt=True, help="Полное имя")
async def main(email: str, password: str, fullname: str) -> None:
    try:
        init_container()
        data = UserCreateDTO(email=email, password=password, fullname=fullname)
        user = await users_service.create_admin(data)
        console.print(f"[bold green]Администратор {user.email} успешно создан![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}[/bold red]")


if __name__ == "__main__":
    main()
