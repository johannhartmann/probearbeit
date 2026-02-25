FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY main.py ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz')"

CMD ["uv", "run", "uvicorn", "ai_messenger_voicemail.app:app", "--host", "0.0.0.0", "--port", "8000"]
