import asyncio
import os
import time
from pathlib import Path
import json
from string import Template

from dotenv import load_dotenv

from reserach.constants import MODELS
from reserach.utils import load_records_from_dataset, get_dataset_path, get_criteria_checks_path, \
    get_project_prompt_path, log_llm_calling
from src.infrastructure.ai.llm.openai_like import OpenAILikeLLM


SYSTEM_PROMPT_TEMPLATE = Template("""
## Роль
Ты — строгий, но справедливый ассистент преподавателя на курсе по программной инженерии.  
Ваша задача — проверить **предоставленный код и дерево проекта** на соответствие **каждому критерию** из списка ниже.

## Критерии
$criteria_section

## Правила оценки
1. Оценивай только то, что реально присутствует в коде и структуре проекта. Не додумывай отсутствующее.
2. Не пиши общих фраз. Каждый комментарий должен ссылаться на конкретный файл, строку или логическую часть проекта (на основе дерева проекта и содержимого ключевых файлов).

## Формат выходных данных
**Верни только валидный JSON-массив** (без пояснений до или после, без markdown-разметки, без лишних пробелов в начале/конце).

Каждый элемент массива — объект с полями:
{
  "id": 534,
  "comment": "строка с аргументированным выводом",
  "is_passed": true | false | null (если критерий не применим в рамках данного кода)
}
""")

def build_system_prompt(criteria_path: Path) -> str:
    with open(criteria_path, "r", encoding="utf-8") as f:
        criteria = json.load(f)

    criteria_section = "\n".join(
        f"=== Критерий {criterion['id']} ====\n{criterion['description']}\n=== Конец критерия ===\n"
        for criterion in criteria
    )

    return SYSTEM_PROMPT_TEMPLATE.substitute(criteria_section=criteria_section)

async def main():
    print("Loading envs...")
    load_dotenv()
    AI_LLM_API_ENDPOINT = os.environ["AI_LLM_API_ENDPOINT"]
    AI_LLM_API_KEY = os.environ["AI_LLM_API_KEY"]

    print("Starting...")
    result = load_records_from_dataset(get_dataset_path())
    print(f"Loaded {len(result)} rows from dataset")

    for project in result:
        with open(get_project_prompt_path(project.id), "r", encoding="utf-8") as f:
            user_prompt = f.read()
        system_prompt = build_system_prompt(project.criteria_path)
        for model in MODELS:
            if os.path.exists(get_criteria_checks_path(project.id, model)):
                print(f"Skip: {model}, {project.repo_url}")
                continue
            llm = OpenAILikeLLM(AI_LLM_API_ENDPOINT, AI_LLM_API_KEY, model, {"temperature": 0})
            print(f"Processing: {model}, {project.repo_url}")
            start_time = time.perf_counter()
            try:
                answer = await llm.run(system_prompt, user_prompt)
            except Exception as exc:
                print(exc)
                continue
            duration = time.perf_counter() - start_time
            log_llm_calling(model, project.id, answer.input_tokens, answer.output_tokens, duration)
            print(f"Usage: input={answer.input_tokens}, output={answer.output_tokens}")
            with open(get_criteria_checks_path(project.id, model), "w", encoding="utf-8") as f:
                f.write(answer.content)


if __name__ == "__main__":
    asyncio.run(main())
