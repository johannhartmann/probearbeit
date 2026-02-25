from datetime import datetime, timezone
import logging

import httpx

from ai_messenger_voicemail.config import Settings
from ai_messenger_voicemail.store import SqliteStore

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, settings: Settings, store: SqliteStore) -> None:
        self._settings = settings
        self._store = store

    async def sync_updates(self) -> int:
        token = self._settings.telegram_bot_token
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN ist nicht gesetzt. Telegram Sync wird uebersprungen.")
            return 0

        base_url = f"https://api.telegram.org/bot{token}"
        current_offset = self._store.get_telegram_offset()
        max_update_id = current_offset
        total_inserted = 0

        try:
            async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
                while True:
                    payload = {
                        "offset": current_offset + 1,
                        "limit": self._settings.telegram_poll_limit,
                        "timeout": 0,
                        "allowed_updates": ["message"],
                    }
                    response = await client.post(f"{base_url}/getUpdates", json=payload)
                    response.raise_for_status()
                    body = response.json()

                    if not body.get("ok"):
                        description = body.get("description", "Unknown Telegram error")
                        raise RuntimeError(f"Telegram API Fehler: {description}")

                    updates = body.get("result", [])
                    if not updates:
                        break

                    for update in updates:
                        update_id = int(update.get("update_id", 0))
                        if update_id <= 0:
                            continue

                        max_update_id = max(max_update_id, update_id)
                        current_offset = max_update_id

                        message = update.get("message")
                        if not isinstance(message, dict):
                            continue
                        if "text" not in message:
                            continue

                        chat = message.get("chat", {})
                        chat_id = int(chat.get("id", 0))
                        text = str(message.get("text", "")).strip()
                        if chat_id == 0 or not text:
                            continue

                        sender_data = message.get("from", {})
                        sender = (
                            sender_data.get("username")
                            or " ".join(
                                part
                                for part in [
                                    sender_data.get("first_name", ""),
                                    sender_data.get("last_name", ""),
                                ]
                                if part
                            )
                            or "Unbekannt"
                        )

                        timestamp_unix = int(message.get("date", 0))
                        timestamp = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)

                        inserted = self._store.store_message(
                            telegram_update_id=update_id,
                            chat_id=chat_id,
                            sender=str(sender),
                            timestamp=timestamp,
                            text=text,
                        )
                        if inserted:
                            total_inserted += 1
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Telegram API nicht erreichbar: {exc}") from exc

        self._store.set_telegram_offset(max_update_id)
        return total_inserted
