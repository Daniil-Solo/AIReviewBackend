### Проверка кода ruff

```bash
uv run ruff check "C:\Users\user\PycharmProjects\backend-adult-platform" --output-format=json --config "C:\Users\user\PycharmProjects\AutoReviewer\src\services\project\linters\pyproject.toml"
```

### Проверка кода

```bash
uv run bandit "C:\Users\user\PycharmProjects\backend-adult-platform" -r -f json --exclude "tests,migrations,venv,env,.venv,__pycache__"
```