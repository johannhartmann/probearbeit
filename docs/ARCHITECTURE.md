# Architekturuebersicht

## Komponenten

- API Layer: FastAPI in `src/ai_messenger_voicemail/app.py`
- Integrationen:
  - Telegram Bot API: `TelegramService`
  - OpenAI Responses API: `LLMService`
  - Twilio Voice/TwiML: `VoiceService`
- Persistenz:
  - SQLite State Store (`SqliteStore`)
  - Tabellen: `state`, `messages`, `call_contexts`

## Sequenzdiagramm

```mermaid
sequenceDiagram
    participant Caller as Caller (Phone)
    participant Twilio as Twilio Voice
    participant API as FastAPI Service
    participant TG as Telegram API
    participant LLM as OpenAI API
    participant DB as SQLite

    Caller->>Twilio: incoming call
    Twilio->>API: POST /twilio/voice/incoming
    API->>TG: getUpdates
    TG-->>API: unread messages
    API->>DB: store messages + offset
    API->>LLM: summarize(messages)
    LLM-->>API: spoken summary
    API->>DB: save call context + mark read
    API-->>Twilio: TwiML (Say + Gather)
    Twilio-->>Caller: reads summary

    Caller->>Twilio: spoken follow-up
    Twilio->>API: POST /twilio/voice/followup
    API->>DB: load context + append turn
    API->>LLM: answer(question, context)
    LLM-->>API: follow-up answer
    API->>DB: append assistant turn
    API-->>Twilio: TwiML (Say + Gather)
    Twilio-->>Caller: reads answer
```

## Sicherheitsaspekte im Prototyp

- Optionale Twilio-Signaturpruefung (`TWILIO_VALIDATE_SIGNATURE=true`)
- Keine Secrets im Code; alles ueber Environment
- Kein ungefilterter Zugriff auf Telegram bei gesetztem `TELEGRAM_ALLOWED_CHAT_ID`

## Betriebsaspekte

- `GET /healthz` fuer Liveness
- `GET /readyz` prueft DB-Zugriff
- K8s-Probes sind entsprechend konfiguriert
