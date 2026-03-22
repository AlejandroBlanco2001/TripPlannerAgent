FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project

# --- runtime ---
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv

COPY main.py config.py ./
COPY db/__init__.py db/agent.py ./db/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
