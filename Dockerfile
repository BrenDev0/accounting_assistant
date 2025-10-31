FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked

COPY src/ /app/src/

EXPOSE 8001

CMD [ "/app/.venv/bin/uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8001" ]