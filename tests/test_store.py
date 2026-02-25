from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai_messenger_voicemail.store import SqliteStore


def test_store_message_and_mark_read(tmp_path: Path) -> None:
    store = SqliteStore(tmp_path / "state.db")

    inserted = store.store_message(
        telegram_update_id=42,
        chat_id=100,
        sender="alice",
        timestamp=datetime.now(timezone.utc),
        text="Hallo",
    )
    duplicate_inserted = store.store_message(
        telegram_update_id=42,
        chat_id=100,
        sender="alice",
        timestamp=datetime.now(timezone.utc),
        text="Hallo",
    )

    unread = store.list_unread_messages(limit=10)

    assert inserted is True
    assert duplicate_inserted is False
    assert len(unread) == 1

    store.mark_messages_read([unread[0].id])
    assert store.list_unread_messages(limit=10) == []


def test_call_context_roundtrip_and_cleanup(tmp_path: Path) -> None:
    store = SqliteStore(tmp_path / "state.db")
    now = datetime.now(timezone.utc)

    store.store_message(
        telegram_update_id=1,
        chat_id=100,
        sender="bob",
        timestamp=now,
        text="Projektstatus gruen",
    )
    messages = store.list_unread_messages(limit=10)
    store.save_call_context("call-x", "summary", messages)
    store.append_conversation_turn("call-x", role="caller", text="Details")
    store.append_conversation_turn("call-x", role="assistant", text="Hier sind die Details")

    context = store.get_call_context("call-x")
    assert context is not None
    assert context.summary == "summary"
    assert len(context.conversation) == 2

    stale = now - timedelta(minutes=400)
    with store._conn() as conn:  # noqa: SLF001 - test-only direct update
        conn.execute("UPDATE call_contexts SET created_at = ? WHERE call_sid = ?", (stale.isoformat(), "call-x"))

    removed = store.cleanup_stale_call_contexts(ttl_minutes=120)
    assert removed == 1
    assert store.get_call_context("call-x") is None
