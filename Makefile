.PHONY: run test lint sync docker-build

sync:
	uv sync

run:
	uv run uvicorn ai_messenger_voicemail.app:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest

lint:
	uv run python -m compileall src

docker-build:
	docker build -t ai-messenger-voicemail:latest .
