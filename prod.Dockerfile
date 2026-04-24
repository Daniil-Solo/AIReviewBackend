FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install uv==0.9.20

COPY pyproject.toml .

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

RUN uv sync --no-install-project --frozen

FROM python:3.12-slim AS production

WORKDIR /app

RUN pip install uv==0.9.20

COPY --from=builder /opt/venv /opt/venv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app

CMD ["uv", "run", "uvicorn", "src.interfaces.api.app:app", "--host", "0.0.0.0", "--port", "8000"]