FROM python:3.12-slim

WORKDIR /app

RUN pip install uv==0.9.20

COPY pyproject.toml  uv.lock ./

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv sync --no-install-project --frozen

COPY . /app

CMD ["uv", "run", "uvicorn", "src.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]