from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class TelegramMessage:
    id: int
    telegram_update_id: int
    chat_id: int
    sender: str
    timestamp: datetime
    text: str

    def as_prompt_line(self, index: int) -> str:
        ts = self.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return f"{index}. {self.sender} | {ts} | {self.text}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TelegramMessage":
        return cls(
            id=int(data["id"]),
            telegram_update_id=int(data["telegram_update_id"]),
            chat_id=int(data["chat_id"]),
            sender=str(data["sender"]),
            timestamp=datetime.fromisoformat(str(data["timestamp"])),
            text=str(data["text"]),
        )


@dataclass(slots=True)
class ConversationTurn:
    role: str
    text: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "text": self.text}


@dataclass(slots=True)
class CallContext:
    call_sid: str
    summary: str
    messages: list[TelegramMessage]
    conversation: list[ConversationTurn]
    created_at: datetime
