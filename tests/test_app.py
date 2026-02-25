from pathlib import Path
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from ai_messenger_voicemail.app import create_app
from ai_messenger_voicemail.config import Settings
from ai_messenger_voicemail.store import SqliteStore


def test_health_and_readiness(client: TestClient) -> None:
    health = client.get("/healthz")
    ready = client.get("/readyz")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}


def test_incoming_without_messages_returns_twiML(client: TestClient) -> None:
    response = client.post("/twilio/voice/incoming", data={"CallSid": "call-1"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "keine ungelesenen Nachrichten" in response.text


def test_followup_without_call_context(client: TestClient) -> None:
    response = client.post(
        "/twilio/voice/followup",
        data={"CallSid": "unknown", "SpeechResult": "Erzaehl mir mehr"},
    )

    assert response.status_code == 200
    assert "kein Kontext" in response.text


def test_twilio_signature_is_enforced_when_enabled(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        app_env="test",
        base_url="http://testserver",
        sqlite_path=tmp_path / "state.db",
        twilio_validate_signature=True,
        twilio_auth_token="secret",
        openai_api_key=None,
        telegram_bot_token=None,
    )
    client = TestClient(create_app(settings))

    response = client.post("/twilio/voice/incoming", data={"CallSid": "call-2"})
    assert response.status_code == 403


def test_incoming_is_idempotent_for_same_call_sid(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    pre_store = SqliteStore(db_path)
    pre_store.store_message(
        telegram_update_id=100,
        chat_id=555,
        sender="alice",
        timestamp=datetime.now(timezone.utc),
        text="Bitte ruf mich spaeter an.",
    )

    settings = Settings(
        _env_file=None,
        app_env="test",
        base_url="http://testserver",
        sqlite_path=db_path,
        openai_api_key=None,
        telegram_bot_token=None,
        twilio_validate_signature=False,
    )
    client = TestClient(create_app(settings))

    first = client.post("/twilio/voice/incoming", data={"CallSid": "call-idempotent"})
    second = client.post("/twilio/voice/incoming", data={"CallSid": "call-idempotent"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert "Bitte ruf mich spaeter an." in first.text
    assert "Bitte ruf mich spaeter an." in second.text


def test_followup_respects_turn_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    pre_store = SqliteStore(db_path)
    pre_store.store_message(
        telegram_update_id=200,
        chat_id=555,
        sender="bob",
        timestamp=datetime.now(timezone.utc),
        text="Statusupdate",
    )
    messages = pre_store.list_unread_messages(limit=10)
    pre_store.save_call_context("call-limit", "summary", messages)
    pre_store.append_conversation_turn("call-limit", role="caller", text="frage 1")
    pre_store.append_conversation_turn("call-limit", role="assistant", text="antwort 1")

    settings = Settings(
        _env_file=None,
        app_env="test",
        base_url="http://testserver",
        sqlite_path=db_path,
        max_followup_turns=1,
        openai_api_key=None,
        telegram_bot_token=None,
        twilio_validate_signature=False,
    )
    client = TestClient(create_app(settings))

    response = client.post(
        "/twilio/voice/followup",
        data={"CallSid": "call-limit", "SpeechResult": "noch eine frage"},
    )

    assert response.status_code == 200
    assert "maximale Anzahl an Rueckfragen" in response.text
