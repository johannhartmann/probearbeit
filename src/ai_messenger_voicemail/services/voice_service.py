from twilio.twiml.voice_response import Gather, VoiceResponse

from ai_messenger_voicemail.config import Settings


class VoiceService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def should_end(self, text: str) -> bool:
        value = text.lower().strip()
        keywords = ["ende", "beenden", "stop", "tschuss", "auf wiederhoeren"]
        return any(keyword in value for keyword in keywords)

    def incoming_response(self, *, summary: str, has_messages: bool, action_url: str) -> str:
        response = VoiceResponse()
        if has_messages:
            response.say(
                "Willkommen. Du hast ungelesene Nachrichten. Ich lese dir jetzt eine Zusammenfassung vor.",
                language=self._settings.twilio_language,
                voice=self._settings.twilio_voice,
            )
            response.pause(length=1)
            response.say(
                summary,
                language=self._settings.twilio_language,
                voice=self._settings.twilio_voice,
            )

            gather = self._followup_gather(action_url)
            gather.say(
                "Du kannst jetzt Rueckfragen stellen, zum Beispiel: Erzaehl mir mehr ueber Nachricht 2.",
                language=self._settings.twilio_language,
                voice=self._settings.twilio_voice,
            )
            response.append(gather)
            response.say(
                "Ich habe keine Rueckfrage gehoert. Auf Wiederhoeren.",
                language=self._settings.twilio_language,
                voice=self._settings.twilio_voice,
            )
            response.hangup()
            return str(response)

        response.say(
            summary,
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        response.say(
            "Auf Wiederhoeren.",
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        response.hangup()
        return str(response)

    def followup_response(self, *, answer: str, action_url: str) -> str:
        response = VoiceResponse()
        response.say(
            answer,
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        gather = self._followup_gather(action_url)
        gather.say(
            "Wenn du noch etwas wissen willst, stelle jetzt eine weitere Frage. "
            "Sage Ende, um aufzulegen.",
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        response.append(gather)
        response.say(
            "Keine weitere Eingabe erkannt. Auf Wiederhoeren.",
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        response.hangup()
        return str(response)

    def goodbye_response(self, text: str = "Alles klar. Auf Wiederhoeren.") -> str:
        response = VoiceResponse()
        response.say(
            text,
            language=self._settings.twilio_language,
            voice=self._settings.twilio_voice,
        )
        response.hangup()
        return str(response)

    def _followup_gather(self, action_url: str) -> Gather:
        return Gather(
            input="speech",
            action=action_url,
            method="POST",
            language=self._settings.twilio_language,
            speech_timeout="auto",
            timeout=5,
        )
