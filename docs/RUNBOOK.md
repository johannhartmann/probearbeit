# Runbook

## Start lokal

```bash
uv sync --extra dev
cp .env.example .env
uv run uvicorn ai_messenger_voicemail.app:app --host 0.0.0.0 --port 8000 --reload
```

## Funktionstest

```bash
./scripts/smoke_test.sh http://127.0.0.1:8000
```

## Tests

```bash
uv run pytest
```

## Deployment lokal (Kind/K3s)

```bash
docker build -t ai-messenger-voicemail:latest .
kubectl apply -k k8s
```

## Troubleshooting

- `403` auf Twilio-Endpunkten
  - Ursache: Signaturvalidierung aktiv, aber URL/Auth-Token nicht korrekt.
  - Pruefen: `TWILIO_VALIDATE_SIGNATURE`, `TWILIO_AUTH_TOKEN`, `BASE_URL`.
- Keine Telegram-Nachrichten
  - Ursache: Bot-Token/Chat-ID falsch oder keine Bot-Nachrichten vorhanden.
  - Pruefen: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_ID`.
- Readiness rot
  - Ursache: DB-Datei nicht beschreibbar.
  - Pruefen: `SQLITE_PATH`, Dateiberechtigungen, Volume-Mount.
