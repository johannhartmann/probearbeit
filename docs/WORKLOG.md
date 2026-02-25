# Arbeitsprotokoll (nachvollziehbar)

## Schritt 1: Basis-MVP

- Grundservice mit FastAPI, Telegram-Abruf, LLM-Summary, Twilio-TwiML
- Dockerfile und erstes K8s-Manifest

## Schritt 2: Haertung und Architektur

- App-Factory eingefuehrt fuer bessere Testbarkeit
- Readiness Endpoint ergaenzt
- Twilio-Signaturpruefung integriert
- URL-Aufbau fuer Webhooks hinter Proxy/Tunnel verbessert
- Conversation-/Context-Handling stabilisiert

## Schritt 3: Qualitaet und Nachweisbarkeit

- Test-Suite mit API-, Store- und Telegram-Service-Tests
- Dokumentation erweitert (Architektur, Demo, Trade-offs)
- Kubernetes-Artefakte aufgeteilt (ConfigMap, Service, Ingress, Kustomize)

## Schritt 4: Abgabe-Finish

- Idempotente Behandlung wiederholter Twilio Incoming-Webhooks je `CallSid`
- Follow-up-Turn-Limit klar getestet
- Requirements-Traceability und Runbook ergaenzt
- CI-Workflow fuer automatisierte Pruefung (Tests + Compile) hinzugefuegt
