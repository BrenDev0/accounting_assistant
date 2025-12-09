FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y git && apt-get clean
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY uv.lock .
COPY pyproject.toml .
RUN uv sync --locked

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv


ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/

CMD ["python", "-m", "src.app.main"]