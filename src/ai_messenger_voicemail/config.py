from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    log_level: str = "INFO"
    base_url: str | None = None
    sqlite_path: Path = Path("data/state.db")
    request_timeout_seconds: float = Field(default=10.0, ge=1.0, le=60.0)

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    telegram_bot_token: str | None = None
    telegram_poll_limit: int = Field(default=50, ge=1, le=100)
    telegram_allowed_chat_id: int | None = None

    twilio_auth_token: str | None = None
    twilio_validate_signature: bool = False
    twilio_voice: str = "Polly.Vicki"
    twilio_language: str = "de-DE"

    max_messages_per_call: int = Field(default=8, ge=1, le=50)
    max_followup_turns: int = Field(default=6, ge=1, le=20)
    call_context_ttl_minutes: int = Field(default=240, ge=5, le=1440)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
