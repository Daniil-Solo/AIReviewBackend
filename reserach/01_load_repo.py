import io
import tempfile
import zipfile
from pathlib import Path
from string import Template

import httpx
import tiktoken
from treeproject import path_content, path_tree

from reserach.utils import get_project_prompt_path, get_dataset_path, load_records_from_dataset
from src.constants.preprocessing import IGNORED_DIRECTORIES, ALLOWED_EXTENSIONS


def is_ignored_dir(p: Path) -> bool:
    return p.name.startswith(".") or p.name in IGNORED_DIRECTORIES


def include_without_ignored_directories(p: Path) -> bool:
    if p.is_file():
        return True
    return not is_ignored_dir(p)


def include_code_only(p: Path) -> bool:
    if p.is_dir() and not is_ignored_dir(p):
        return True
    return p.is_file() and f".{p.name.split('.')[-1]}" in ALLOWED_EXTENSIONS


PROJECT_PROMPT_TEMPLATE = Template("""
## Структура проекта
```
$project_tree
```

## Контент проекта
$project_content
""")


def create_project_prompt(project_zip_file: bytes) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(io.BytesIO(project_zip_file)) as zf:
            zf.extractall(temp_dir)
            temp_dir_path = Path(temp_dir)
            children = [p for p in temp_dir_path.iterdir()]
            if len(children) == 1 and children[0].is_dir():
                project_root_path = children[0]
            else:
                project_root_path = temp_dir_path
            project_tree = path_tree(project_root_path, include=include_without_ignored_directories)
            project_content = path_content(project_root_path, include=include_code_only, encoding="utf-8")
            return PROJECT_PROMPT_TEMPLATE.substitute(project_tree=project_tree, project_content=project_content)


def load_repository(repo_url: str, branch: str) -> bytes:
    new_url = repo_url.replace("github.com", "codeload.github.com")
    with httpx.Client() as client:
        response = client.get(f"{new_url}/zip/refs/heads/{branch}")
        response.raise_for_status()
        return response.content


def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))



if __name__ == "__main__":
    print("Starting...")
    result = load_records_from_dataset(get_dataset_path())
    print(f"Loaded {len(result)} rows from dataset")
    for item in result:
        print(f"Loading repo: {item.repo_url}, {item.branch}")
        repository_zip_bytes = load_repository(item.repo_url, item.branch)
        print(f"Generating prompt")
        prompt = create_project_prompt(repository_zip_bytes)
        count = count_tokens(prompt)
        print(f"Prompt is about {count} tokens")
        prompt_path = get_project_prompt_path(item.id)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved in {prompt_path}")
        print("=====")