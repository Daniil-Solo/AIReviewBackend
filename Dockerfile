FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .

RUN uv sync --no-dev --no-editable

COPY src/ src/

CMD ["uv", "run", "uvicorn", "src.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]