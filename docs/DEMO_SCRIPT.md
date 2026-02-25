# Demo Script (15 Minuten)

## Vorbereitung (2-3 Minuten)

1. Service starten (`uv run uvicorn ...`).
2. Tunnel aktivieren (`ngrok http 8000`).
3. Twilio-Webhook auf `/twilio/voice/incoming` setzen.
4. Testnachrichten an Telegram-Bot senden.

## Live-Flow (8-10 Minuten)

1. Eingehenden Anruf starten.
2. Begruessung + Zusammenfassung vorlesen lassen.
3. Rueckfrage stellen: "Erzaehl mir mehr ueber Nachricht 2".
4. Zweite Rueckfrage: "Wiederhole die Zusammenfassung".
5. Beenden mit "Ende".

## Architektur-Review (3-5 Minuten)

- Warum SQLite fuer Prototyp
- Warum Polling fuer Telegram im MVP
- Wie Signaturpruefung und Env-Konfiguration umgesetzt sind
- Welche Schritte fuer Produktionsreife geplant sind
