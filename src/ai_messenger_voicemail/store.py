import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai_messenger_voicemail.models import CallContext, ConversationTurn, TelegramMessage


class SqliteStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_update_id INTEGER NOT NULL UNIQUE,
                    chat_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    text TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS call_contexts (
                    call_sid TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    messages_json TEXT NOT NULL,
                    conversation_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO state(key, value) VALUES ('telegram_offset', '0')"
            )

    def ping(self) -> None:
        with self._conn() as conn:
            conn.execute("SELECT 1")

    def get_telegram_offset(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT value FROM state WHERE key = 'telegram_offset'"
            ).fetchone()
            if row is None:
                return 0
            return int(row["value"])

    def set_telegram_offset(self, offset: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO state(key, value) VALUES ('telegram_offset', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(offset),),
            )

    def store_message(
        self,
        *,
        telegram_update_id: int,
        chat_id: int,
        sender: str,
        timestamp: datetime,
        text: str,
    ) -> bool:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO messages(
                    telegram_update_id, chat_id, sender, ts, text
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    telegram_update_id,
                    chat_id,
                    sender,
                    timestamp.isoformat(),
                    text,
                ),
            )
            return cursor.rowcount > 0

    def list_unread_messages(
        self,
        *,
        limit: int,
        allowed_chat_id: int | None = None,
    ) -> list[TelegramMessage]:
        query = (
            "SELECT id, telegram_update_id, chat_id, sender, ts, text "
            "FROM messages WHERE is_read = 0"
        )
        params: list[object] = []
        if allowed_chat_id is not None:
            query += " AND chat_id = ?"
            params.append(allowed_chat_id)
        query += " ORDER BY ts DESC LIMIT ?"
        params.append(limit)

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()

        result: list[TelegramMessage] = []
        for row in rows:
            result.append(
                TelegramMessage(
                    id=int(row["id"]),
                    telegram_update_id=int(row["telegram_update_id"]),
                    chat_id=int(row["chat_id"]),
                    sender=str(row["sender"]),
                    timestamp=datetime.fromisoformat(str(row["ts"])),
                    text=str(row["text"]),
                )
            )
        return result

    def mark_messages_read(self, ids: list[int]) -> None:
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        with self._conn() as conn:
            conn.execute(
                f"UPDATE messages SET is_read = 1 WHERE id IN ({placeholders})",
                ids,
            )

    def save_call_context(
        self,
        call_sid: str,
        summary: str,
        messages: list[TelegramMessage],
    ) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO call_contexts(call_sid, summary, messages_json, conversation_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(call_sid) DO UPDATE SET
                  summary = excluded.summary,
                  messages_json = excluded.messages_json,
                  conversation_json = excluded.conversation_json,
                  created_at = excluded.created_at
                """,
                (
                    call_sid,
                    summary,
                    json.dumps([m.to_dict() for m in messages], ensure_ascii=True),
                    json.dumps([], ensure_ascii=True),
                    created_at,
                ),
            )

    def get_call_context(self, call_sid: str) -> CallContext | None:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT summary, messages_json, conversation_json, created_at
                FROM call_contexts
                WHERE call_sid = ?
                """,
                (call_sid,),
            ).fetchone()

        if row is None:
            return None

        messages_raw = json.loads(str(row["messages_json"]))
        conversation_raw = json.loads(str(row["conversation_json"]))

        return CallContext(
            call_sid=call_sid,
            summary=str(row["summary"]),
            messages=[TelegramMessage.from_dict(item) for item in messages_raw],
            conversation=[
                ConversationTurn(role=str(item["role"]), text=str(item["text"]))
                for item in conversation_raw
            ],
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )

    def append_conversation_turn(self, call_sid: str, role: str, text: str) -> list[ConversationTurn]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT conversation_json FROM call_contexts WHERE call_sid = ?",
                (call_sid,),
            ).fetchone()
            if row is None:
                return []
            conversation = json.loads(str(row["conversation_json"]))
            conversation.append({"role": role, "text": text})
            conn.execute(
                "UPDATE call_contexts SET conversation_json = ? WHERE call_sid = ?",
                (json.dumps(conversation, ensure_ascii=True), call_sid),
            )

        return [
            ConversationTurn(role=str(item["role"]), text=str(item["text"]))
            for item in conversation
        ]

    def cleanup_stale_call_contexts(self, *, ttl_minutes: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=ttl_minutes)
        with self._conn() as conn:
            cursor = conn.execute(
                "DELETE FROM call_contexts WHERE created_at < ?",
                (cutoff.isoformat(),),
            )
            return cursor.rowcount
