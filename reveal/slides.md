# Probearbeit Pitch
## Junior Developer Edition

**ehrlich, lernstark, technisch sauber**

---

## Wer ich hier bin

- frisch von der Uni
- viel Ehrgeiz und Freude an Technik
- Fokus auf strukturierte, belastbare Umsetzung

**Botschaft:** Junior heisst nicht "nur Theorie".

---

## 3-Minuten Pitch (Agenda)

1. Problem und Ergebnis
2. Architektur kurz und klar
3. Robustheit statt nur Happy Path
4. Trade-offs im MVP
5. Produktionsnaechste Schritte

---

## 0:00-0:50
### Problem + End-to-End Loesung

- Anruf kommt rein
- Telegram unread abrufen
- LLM fasst zusammen
- Twilio liest vor
- Rueckfragen im gleichen Call

**One-liner:**
"Funktionaler Voice-Prototyp mit klarer Integrationsarchitektur."

---

## 0:50-1:55
### Was ich robust gebaut habe

- Twilio Signature Validation
- Idempotenz fuer Incoming ueber `CallSid`
- Fallbacks bei API/LLM-Problemen
- Health + Readiness fuer Betrieb

**Lernpunkt:**
Zuverlaessigkeit ist im Voice-Flow genauso wichtig wie Features.

---

## 1:55-3:00
### Delivery + bewusstes MVP

- Tests + CI + Docker + Kubernetes
- Runbook + Smoke-Test + Traceability

**Bewusste Trade-offs**
- `Gather` statt low-latency media streaming
- SQLite statt Postgres/Redis

---

## Naechste 3 Schritte (produktion)

1. Telegram webhook/event-driven ingress
2. Postgres/Redis fuer skalierbaren state
3. Observability: tracing, metriken, alerts

---

## Q&A 1-5

1. Warum Telegram? -> schnellster stabiler MVP-Einstieg
2. Warum Polling? -> weniger Komplexitaet, spaeter Webhook
3. Warum SQLite? -> schnell + reproduzierbar lokal
4. Retries? -> idempotent per `CallSid`
5. Security? -> Signaturvalidierung + Secret-only config

---

## Q&A 6-10

6. LLM faellt aus? -> regelbasierter fallback
7. Testtiefe? -> API, store, sync, security, limits
8. Groesste Luecke? -> multi-instance state
9. Betriebssetup? -> K8s probes + CI + smoke-test
10. Wichtigste Entscheidung? -> klare Trennung von concerns

---

## Ehrliche KI-Position

- KI als Beschleuniger fuer Boilerplate/Review
- Architektur, Fehleranalyse, Tests, finale Entscheidungen selbst
- ich kann jeden Kernpfad technisch erklaeren

---

## Closing (20 Sekunden)

"Ich habe als Junior einen vollstaendigen, testbaren End-to-End-Prototyp geliefert. Ich lerne schnell, arbeite strukturiert und kann Entscheidungen transparent begruenden. Genau darauf will ich im Team aufbauen."

