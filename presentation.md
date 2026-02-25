# Praesentationsvorbereitung (Junior Developer Edition)

## Zielbild fuer deinen Auftritt

Du trittst auf als:
- frisch von der Uni
- sehr motiviert, technisch neugierig, lernst schnell
- ehrlich bei Grenzen, stark bei Struktur und Umsetzung

Wichtig: Nicht klein machen. Du darfst klar sagen, was du gut geloest hast.

---

## Teil 1: 3-Minuten-Version (Wortlaut + Timing)

## 0:00-0:20 - Einstieg (Selbstbild + Ergebnis)

Sprechtext:
"Ich bin frisch von der Uni und habe in dieser Probearbeit einen kompletten End-to-End-Prototyp umgesetzt: eingehender Telefonanruf, automatischer Telegram-Abruf ungelesener Nachrichten, LLM-Zusammenfassung und sprachliche Rueckfragen im laufenden Call."

Wirkung:
- Du setzt direkt den Rahmen: Junior, aber lieferfaehig.

## 0:20-0:50 - Ein Satz zur Architektur

Sprechtext:
"Der Kern ist ein klar getrennter Service-Aufbau: FastAPI orchestriert den Flow, Telegram liefert Nachrichten, OpenAI fasst zusammen und beantwortet Rueckfragen, Twilio uebernimmt die Sprachein- und ausgabe ueber Webhooks und TwiML."

Wirkung:
- Du wirkst strukturiert statt nur "ich habe irgendwas gebaut".

## 0:50-1:25 - Was du bewusst robust gebaut hast

Sprechtext:
"Mir war wichtig, nicht nur den Happy Path zu bauen. Deshalb habe ich Twilio-Signaturvalidierung integriert, den Incoming-Webhook idempotent ueber `CallSid` gemacht, Fallbacks fuer API/LLM-Fehler eingebaut und Health/Readiness-Endpunkte fuer den Betrieb umgesetzt."

Wirkung:
- Zeigt Reife im Denken und echtes Engineering-Verstaendnis.

## 1:25-1:55 - Nachweisbarkeit und Delivery

Sprechtext:
"Ich habe die Abgabe bewusst reproduzierbar aufgebaut: lokales Setup mit `uv`, automatisierte Tests fuer API-Flow, Telegram-Sync und Store-Lifecycle, plus CI-Checks, Dockerfile und Kubernetes-Manifeste mit ConfigMap, Secret, Ingress und Probes."

Wirkung:
- Du zeigst, dass du nicht nur Code, sondern auch Delivery kannst.

## 1:55-2:30 - Ehrliche Trade-offs

Sprechtext:
"Ich habe pragmatische MVP-Entscheidungen getroffen: Twilio `Gather` statt Low-Latency-Media-Streaming und SQLite statt verteilter Persistenz. Das war bewusst, um in kurzer Zeit einen stabilen End-to-End-Prototyp zu liefern."

Wirkung:
- Keine Ausreden, sondern priorisierte Entscheidungen.

## 2:30-3:00 - Lernkurve + naechste Schritte

Sprechtext:
"Ich habe bei der Umsetzung viel gelernt, vor allem zu Webhook-Robustheit und State-Handling in Sprachflows. Als naechste Schritte fuer Produktion sehe ich: Telegram webhook/event-driven statt Polling, Postgres/Redis fuer skalierbaren Zustand und Observability mit Tracing und Metriken."

Optionaler Zusatzsatz (wenn passend):
"KI habe ich als Beschleuniger genutzt, aber Architekturentscheidungen, Fehleranalyse, Tests und finale Umsetzung habe ich selbst verantwortet."

Wirkung:
- Ehrgeizig, reflektiert, lernstark.

---

## Kurzversion fuer Nervositaet (60 Sek.)

"Ich bin Junior-Entwickler und habe einen funktionalen End-to-End-Prototyp fuer einen AI-Messenger-Anrufbeantworter gebaut. Der Flow ist: eingehender Anruf, Telegram unread abrufen, LLM-Zusammenfassung erzeugen, per Sprache vorlesen und Rueckfragen beantworten. Architektur ist klar getrennt in Orchestrierung, Integrationen und Persistenz. Ich habe bewusst robuste Punkte eingebaut, z. B. Signaturvalidierung, Idempotenz ueber `CallSid`, Fallbacks und Readiness. Die Abgabe ist reproduzierbar mit Tests, CI, Docker und Kubernetes."

---

## Teil 2: 10 typische Rueckfragen mit starken 20-Sekunden-Antworten

## 1) "Warum Telegram Bot API?"

Antwort:
"Fuer den Prototyp war Telegram die schnellste und stabilste Integrationsroute ohne OAuth-Komplexitaet. Ich wollte die Zeit in den Kernflow investieren, nicht in Provider-Onboarding."

## 2) "Warum Polling statt Webhook?"

Antwort:
"Polling war im MVP die pragmatischste Variante fuer reproduzierbares lokales Testen. Der naechste Schritt fuer Produktion ist klar: eventgetriebener Webhook-Eingang."

## 3) "Warum SQLite?"

Antwort:
"SQLite ist fuer den Prototyp ideal: schnell, transparent, ohne extra Betriebsaufwand. Fuer Mehrinstanzbetrieb wuerde ich auf Postgres/Redis wechseln."

## 4) "Wie gehst du mit Twilio-Retries um?"

Antwort:
"Incoming ist idempotent ueber `CallSid`. Wenn derselbe Webhook erneut kommt, nutze ich den vorhandenen Kontext und vermeide doppeltes Verarbeiten."

## 5) "Wie sieht Security aus?"

Antwort:
"Twilio-Signaturvalidierung ist integriert und per Env aktivierbar. Secrets liegen nicht im Code, sondern in Environment/K8s Secret."

## 6) "Was passiert bei LLM-Ausfall?"

Antwort:
"Dann faellt der Flow nicht aus: ich habe regelbasierte Fallback-Zusammenfassungen und Follow-up-Antworten, damit der Call sinnvoll weitergeht."

## 7) "Wie hast du getestet?"

Antwort:
"Ich habe die zentralen Verhaltensfaelle getestet: Health/Readiness, API-Flow, Signaturfaelle, Telegram-Sync, Store-Lifecycle, Idempotenz und Turn-Limits."

## 8) "Groesste aktuelle Luecke?"

Antwort:
"Skalierbares Multi-User-State-Management. Das ist fuer den MVP bewusst schlank gehalten und der Produktionspfad ist klar definiert."

## 9) "Was macht dich als Junior stark fuer so ein Thema?"

Antwort:
"Ich lerne schnell, arbeite strukturiert und dokumentiere Entscheidungen sauber. In dieser Arbeit sieht man, dass ich nicht nur Features baue, sondern auch Robustheit und Betrieb mitdenke."

## 10) "Was waere dein erster Produktionsschritt?"

Antwort:
"State-Schicht haerten: Postgres/Redis, saubere Session-Isolation und bessere Observability. Das reduziert Betriebsrisiko am staerksten."

---

## Mini-Coaching fuer Auftreten (praxisnah)

1. Sprich in kurzen Saetzen, nicht zu schnell.
2. Nenne bei jeder Entscheidung kurz "Warum".
3. Wenn du etwas nicht weisst: "Gute Frage, mein aktueller Ansatz waere ...".
4. Sag einmal aktiv: "Das war eine bewusste MVP-Entscheidung.".
5. Nutze das Wort "gelernt" gezielt 1-2 Mal, nicht dauernd.

---

## 20-Sekunden Closing (Junior + ambitioniert)

"Ich habe gezeigt, dass ich als Junior einen kompletten, testbaren End-to-End-Prototyp liefern kann. Mir ist wichtig, schnell zu lernen, sauber zu arbeiten und Entscheidungen transparent zu begruenden. Genau diesen Stil moechte ich im Team weiter ausbauen."

---

## Letzter Selbstcheck vor dem Gespraech

1. Kann ich den gesamten Flow in 20 Sekunden erklaeren?
2. Kann ich 2 Trade-offs plus Produktionspfad nennen?
3. Kann ich Signaturvalidierung + Idempotenz konkret beschreiben?
4. Klinge ich neugierig und lernorientiert, aber trotzdem praezise?
5. Habe ich einen klaren Schlusssatz, den ich sicher sagen kann?
