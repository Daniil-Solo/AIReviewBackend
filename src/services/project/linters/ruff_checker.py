import subprocess
from pathlib import Path
from pprint import pprint


def run_ruff_on_project(project_path: Path) -> dict:
    """
    Запускает ruff на проекте с любыми зависимостями.
    Никакие библиотеки проекта не устанавливаются.
    """
    try:
        # ruff анализирует только файлы .py
        result = subprocess.run(
            ["ruff", "check", str(project_path), "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=60,  # даже большой проект анализируется быстро
        )

        if result.returncode == 0:
            return {"success": True, "issues": []}

        import json

        issues = json.loads(result.stdout)
        return {"success": False, "issues": issues}

    except FileNotFoundError:
        return {"success": False, "error": "ruff not installed. Run: pip install ruff"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Analysis timeout (project too large?)"}


# Использование для проекта с transformers
result = run_ruff_on_project(Path(r"C:\Users\user\PycharmProjects\Avito-analytics\Parsing"))
pprint(result)
