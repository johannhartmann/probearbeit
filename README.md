# AI-Powered Messenger-Anrufbeantworter

Prototyp fuer die Probearbeit 02/2026: eingehender Telefonanruf -> Abruf ungelesener Messenger-Nachrichten -> LLM-Zusammenfassung -> Sprachausgabe mit Rueckfragen.

## 1. Zielbild

Der Dienst nimmt einen Voice-Webhook (Twilio) entgegen, synchronisiert ungelesene Telegram-Nachrichten, erstellt eine kompakte Zusammenfassung per LLM und liest sie vor. Im gleichen Anruf koennen Rueckfragen per Sprache gestellt werden.

## 2. Erfuellung der Aufgabenstellung

- Telefonanruf entgegennehmen: `POST /twilio/voice/incoming`
- Ungelesene Messenger-Nachrichten abrufen: Telegram `getUpdates` + lokale unread-Logik
- LLM-Zusammenfassung: OpenAI Responses API mit strukturiertem Prompt
- Sprache an Anrufer zurueckgeben: TwiML `Say` + `Gather`
- Bidirektionale Interaktion: Follow-up Endpoint `POST /twilio/voice/followup`
- Fehlerbehandlung: API-Fehler, keine Nachrichten, unverstaendliche Eingabe, fehlender Kontext
- Containerisierung: `Dockerfile`
- Deployment-Manifest: Kubernetes unter `k8s/`
- Konfig via Env Vars: siehe `.env.example`
- Health/Readiness: `/healthz`, `/readyz`

## 3. Architektur

Details: [docs/ARCHITECTURE.md](/Users/johann/src/ml/probearbeit/docs/ARCHITECTURE.md)
Runbook: [docs/RUNBOOK.md](/Users/johann/src/ml/probearbeit/docs/RUNBOOK.md)
Traceability: [docs/REQUIREMENTS_TRACE.md](/Users/johann/src/ml/probearbeit/docs/REQUIREMENTS_TRACE.md)

Kernkomponenten:

- `FastAPI` API-Layer
- `TelegramService` Integration + Sync
- `LLMService` Zusammenfassung und Follow-up-Antworten
- `VoiceService` TwiML-Erzeugung
- `SqliteStore` Persistenz fuer Offsets, unread, Call-Kontexte
- `Twilio Signature Validation` (optional aktivierbar)

## 4. Lokales Setup mit uv

```bash
uv venv .venv
uv sync
cp .env.example .env
```

`.env` fuellen:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TWILIO_AUTH_TOKEN` (wenn Signaturpruefung aktiv)
- `BASE_URL` (oeffentliche URL fuer Webhooks)

## 5. Service starten

```bash
uv run uvicorn ai_messenger_voicemail.app:app --host 0.0.0.0 --port 8000 --reload
```

Optional Tunnel:

```bash
ngrok http 8000
```

Dann in Twilio Voice Webhook konfigurieren:

- `https://<public-host>/twilio/voice/incoming` (POST)

## 6. API-Endpunkte

- `GET /healthz`: Liveness
- `GET /readyz`: Readiness (DB erreichbar)
- `POST /telegram/sync`: manueller Telegram-Sync
- `POST /twilio/voice/incoming`: Einstiegspunkt eingehender Call
- `POST /twilio/voice/followup`: Rueckfragen im laufenden Call

## 7. Tests

```bash
uv run pytest
```

Abgedeckt:

- Health/Readiness
- Incoming/Follow-up Voice Flow
- Signaturpruefung (403 ohne gueltige Signatur)
- Telegram-Sync Parsing/Persistenz
- Store-Roundtrip und Cleanup
- Idempotenz fuer wiederholte Incoming-Webhooks
- Begrenzung der maximalen Rueckfragen

CI-Workflow:

- GitHub Actions unter `.github/workflows/ci.yml` (Sync, Tests, Compile-Check)

## 8. Docker

```bash
docker build -t ai-messenger-voicemail:latest .
docker run --rm -p 8000:8000 --env-file .env ai-messenger-voicemail:latest
```

## 9. Kubernetes (lokal, z. B. Kind)

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
# optional
kubectl apply -f k8s/ingress.yaml
```

Oder via Kustomize:

```bash
kubectl apply -k k8s
```

## 10. Demo-Ablauf

Siehe [docs/DEMO_SCRIPT.md](/Users/johann/src/ml/probearbeit/docs/DEMO_SCRIPT.md).

Zusatz: lokaler Smoke-Test via `./scripts/smoke_test.sh`.

## 11. Grenzen und bewusste Trade-offs

- TTS/STT laeuft ueber Twilio `Gather` (kein low-latency Media-Stream).
- SQLite ist fuer Prototyp und lokale Deployments ausreichend.
- Telegram "ungelesen" ist im Prototyp service-lokal modelliert.

## 12. Ausbauschritte fuer Produktion

- Persistenz auf Postgres/Redis
- Eventgetriebene Telegram-Webhooks statt Polling
- Bessere Multi-User-Isolation (Mandantenmodell)
- Observability (Tracing, Metriken, Alerting)
