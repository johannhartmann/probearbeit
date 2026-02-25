from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai_messenger_voicemail.app import create_app
from ai_messenger_voicemail.config import Settings


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        app_env="test",
        base_url="http://testserver",
        sqlite_path=tmp_path / "state.db",
        openai_api_key=None,
        telegram_bot_token=None,
        twilio_validate_signature=False,
        twilio_auth_token=None,
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    app = create_app(test_settings)
    return TestClient(app)
