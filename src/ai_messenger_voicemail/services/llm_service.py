import json
import logging
import re

from openai import AsyncOpenAI

from ai_messenger_voicemail.config import Settings
from ai_messenger_voicemail.models import ConversationTurn, TelegramMessage

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def summarize_messages(self, messages: list[TelegramMessage]) -> str:
        if not messages:
            return "Aktuell liegen keine ungelesenen Nachrichten vor."

        if self._client is None:
            logger.warning("OPENAI_API_KEY fehlt. Nutze regelbasierte Fallback-Zusammenfassung.")
            return self._fallback_summary(messages)

        prompt_lines = [msg.as_prompt_line(idx) for idx, msg in enumerate(messages, start=1)]
        prompt = "\n".join(prompt_lines)

        try:
            response = await self._client.responses.create(
                model=self._settings.openai_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Du bist ein deutschsprachiger Assistent fuer Telefonzusammenfassungen. "
                            "Fasse Messenger-Nachrichten kompakt und gut vorlesbar zusammen. "
                            "Format je Zeile: Nachricht N: Absender -> Zeitpunkt -> Zusammenfassung. "
                            "Verdichte Dopplungen und priorisiere wichtige Inhalte."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Fasse diese ungelesenen Nachrichten fuer einen Sprachanruf zusammen:\n"
                            f"{prompt}"
                        ),
                    },
                ],
                max_output_tokens=450,
            )
            answer = response.output_text.strip()
            if answer:
                return answer
        except Exception:  # noqa: BLE001
            logger.exception("LLM-Zusammenfassung fehlgeschlagen. Nutze Fallback.")

        return self._fallback_summary(messages)

    async def answer_followup(
        self,
        question: str,
        messages: list[TelegramMessage],
        summary: str,
        conversation: list[ConversationTurn],
    ) -> str:
        if not messages:
            return "Es sind aktuell keine Nachrichten im Kontext dieses Anrufs vorhanden."

        if self._client is None:
            return self._fallback_followup(question, messages, summary)

        history = "\n".join(f"{item.role}: {item.text}" for item in conversation[-8:])
        messages_block = "\n".join(msg.as_prompt_line(idx) for idx, msg in enumerate(messages, start=1))

        try:
            response = await self._client.responses.create(
                model=self._settings.openai_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Du bist ein sprachbasierter Messenger-Assistent auf Deutsch. "
                            "Antworte kurz, praezise und auf die konkrete Rueckfrage. "
                            "Wenn der Nutzer auf Nachrichtsnummern verweist, nutze genau diese Inhalte."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "question": question,
                                "summary": summary,
                                "messages": messages_block,
                                "history": history,
                            },
                            ensure_ascii=True,
                        ),
                    },
                ],
                max_output_tokens=350,
            )
            answer = response.output_text.strip()
            if answer:
                return answer
        except Exception:  # noqa: BLE001
            logger.exception("LLM-Antwort fuer Rueckfrage fehlgeschlagen. Nutze Fallback.")

        return self._fallback_followup(question, messages, summary)

    def _fallback_summary(self, messages: list[TelegramMessage]) -> str:
        lines: list[str] = []
        for index, msg in enumerate(messages, start=1):
            timestamp = msg.timestamp.strftime("%d.%m.%Y %H:%M")
            preview = msg.text.replace("\n", " ")
            if len(preview) > 120:
                preview = f"{preview[:117]}..."
            lines.append(f"Nachricht {index}: {msg.sender} -> {timestamp} -> {preview}.")
        return " ".join(lines)

    def _fallback_followup(self, question: str, messages: list[TelegramMessage], summary: str) -> str:
        match = re.search(r"(?:nachricht|nummer)\s*(\d+)", question.lower())
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(messages):
                msg = messages[idx]
                timestamp = msg.timestamp.strftime("%d.%m.%Y %H:%M")
                return f"Nachricht {idx + 1} von {msg.sender} um {timestamp}: {msg.text}"
            return f"Ich finde Nachricht {idx + 1} nicht. Es liegen nur {len(messages)} Nachrichten vor."

        if any(keyword in question.lower() for keyword in ["wiederhol", "zusammenfass", "nochmal"]):
            return f"Ich wiederhole die Zusammenfassung: {summary}"

        return "Ich kann dazu nur auf Basis der vorhandenen Nachrichten antworten. Bitte nenne eine Nachrichtsnummer."
