# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy only the virtual environment and source code
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/

EXPOSE 8001

CMD [ "/app/.venv/bin/fastapi", "run", "src/api/server.py", "--port", "8001", "--forwarded-allow-ips='*'", "--root-path", "/99b5792d-c38a-4e49-9207-a3fa547905ae" ]