import asyncio
from pathlib import Path

import pytest

from ai_messenger_voicemail.config import Settings
from ai_messenger_voicemail.services import telegram_service as telegram_module
from ai_messenger_voicemail.services.telegram_service import TelegramService
from ai_messenger_voicemail.store import SqliteStore


class _DummyResponse:
    def __init__(self, body: dict) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._body


class _DummyClient:
    def __init__(self, responses: list[dict], **_: object) -> None:
        self._responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False

    async def post(self, url: str, json: dict):  # noqa: A002
        assert url.endswith("/getUpdates")
        assert "offset" in json
        if not self._responses:
            return _DummyResponse({"ok": True, "result": []})
        return _DummyResponse(self._responses.pop(0))


@pytest.mark.parametrize("allowed_chat_id", [None, 555])
def test_sync_updates_stores_new_messages(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, allowed_chat_id: int | None) -> None:
    responses = [
        {
            "ok": True,
            "result": [
                {
                    "update_id": 10,
                    "message": {
                        "date": 1739962800,
                        "text": "Erste Nachricht",
                        "chat": {"id": 555},
                        "from": {"username": "alice"},
                    },
                },
                {
                    "update_id": 11,
                    "message": {
                        "date": 1739966400,
                        "text": "Zweite Nachricht",
                        "chat": {"id": 777},
                        "from": {"first_name": "Bob"},
                    },
                },
            ],
        },
        {"ok": True, "result": []},
    ]

    monkeypatch.setattr(
        telegram_module.httpx,
        "AsyncClient",
        lambda **kwargs: _DummyClient(responses, **kwargs),
    )

    settings = Settings(
        _env_file=None,
        sqlite_path=tmp_path / "state.db",
        telegram_bot_token="token",
        telegram_allowed_chat_id=allowed_chat_id,
        openai_api_key=None,
        twilio_validate_signature=False,
    )
    store = SqliteStore(tmp_path / "state.db")
    service = TelegramService(settings, store)

    inserted = asyncio.run(service.sync_updates())

    assert inserted == 2
    unread = store.list_unread_messages(limit=10, allowed_chat_id=allowed_chat_id)
    if allowed_chat_id is None:
        assert len(unread) == 2
    else:
        assert len(unread) == 1
    assert store.get_telegram_offset() == 11
