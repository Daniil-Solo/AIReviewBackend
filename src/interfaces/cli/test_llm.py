import click
from rich.console import Console

from src.infrastructure.llm.base import Message
from src.infrastructure.llm.openai_like import OpenAILikeLLM


console = Console()


@click.command()
@click.option("--text", "-t", type=click.STRING, default="Привет! Ты кто?", help="Сообщение к модели")
def main(text: str) -> None:
    model = "qwen/qwen3-235b-a22b-2507"

    llm = OpenAILikeLLM("base_url", "api_key", model)

    messages = [Message(role="user", content=text)]

    answer = llm.answer(messages)

    console.print(f"[bold green]Сгенерирован текст: {answer.content} [/bold green]")
    console.print(f"[bold green]Входные токены: {answer.in_tokens} [/bold green]")
    console.print(f"[bold green]Выходные токены: {answer.out_tokens} [/bold green]")


@click.command()
@click.option("--text", "-t", type=click.STRING, default="Привет! Ты кто?", help="Сообщение к модели")
def structured_main(text: str) -> None:
    model = "mistralai/mistral-small-24b-instruct-2501"

    llm = OpenAILikeLLM("base_url", "api_key", model)

    messages = [Message(role="user", content=text)]

    answer = llm.answer(
        messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "model-card",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the model"},
                        "vendor": {"type": "string", "description": "Vendor or organization that provides the model"},
                        "context_length": {"type": "integer", "description": "Maximum context length in tokens"},
                    },
                    "required": ["name", "vendor", "context_length"],
                    "additionalProperties": False,
                },
            },
        },
    )

    console.print(f"[bold green]Сгенерирован текст: {answer.content} [/bold green]")
    console.print(f"[bold green]Входные токены: {answer.in_tokens} [/bold green]")
    console.print(f"[bold green]Выходные токены: {answer.out_tokens} [/bold green]")


if __name__ == "__main__":
    main()
