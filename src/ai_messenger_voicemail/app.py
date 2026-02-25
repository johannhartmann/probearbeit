import logging

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from ai_messenger_voicemail.config import Settings, get_settings
from ai_messenger_voicemail.security import build_public_url, validate_twilio_signature
from ai_messenger_voicemail.services.llm_service import LLMService
from ai_messenger_voicemail.services.telegram_service import TelegramService
from ai_messenger_voicemail.services.voice_service import VoiceService
from ai_messenger_voicemail.store import SqliteStore

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    store = SqliteStore(app_settings.sqlite_path)
    telegram_service = TelegramService(app_settings, store)
    llm_service = LLMService(app_settings)
    voice_service = VoiceService(app_settings)

    app = FastAPI(title="AI Messenger Voicemail", version="0.2.0")

    @app.get("/healthz")
    def healthz() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/readyz")
    def readyz() -> JSONResponse:
        try:
            store.ping()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Readiness fehlgeschlagen")
            return JSONResponse({"status": "error", "reason": str(exc)}, status_code=503)
        return JSONResponse({"status": "ready"})

    @app.post("/telegram/sync")
    async def telegram_sync() -> JSONResponse:
        inserted = await telegram_service.sync_updates()
        unread_count = len(
            store.list_unread_messages(
                limit=100,
                allowed_chat_id=app_settings.telegram_allowed_chat_id,
            )
        )
        return JSONResponse({"inserted": inserted, "unread": unread_count})

    @app.post("/twilio/voice/incoming")
    async def twilio_voice_incoming(request: Request) -> Response:
        form = await request.form()
        if not validate_twilio_signature(request, form, app_settings):
            logger.warning("Twilio-Signaturpruefung fehlgeschlagen (incoming).")
            return Response(status_code=403)

        call_sid = str(form.get("CallSid", "unknown-call"))
        followup_url = build_public_url(request, app_settings, "/twilio/voice/followup")

        store.cleanup_stale_call_contexts(ttl_minutes=app_settings.call_context_ttl_minutes)
        existing_context = store.get_call_context(call_sid)
        if existing_context is not None:
            logger.info("Wiederholter Incoming-Webhook fuer CallSid=%s erkannt. Nutze bestehenden Kontext.", call_sid)
            twiml = voice_service.incoming_response(
                summary=existing_context.summary,
                has_messages=bool(existing_context.messages),
                action_url=followup_url,
            )
            return PlainTextResponse(content=twiml, media_type="application/xml")

        try:
            await telegram_service.sync_updates()
            unread_messages = store.list_unread_messages(
                limit=app_settings.max_messages_per_call,
                allowed_chat_id=app_settings.telegram_allowed_chat_id,
            )
            summary = await llm_service.summarize_messages(unread_messages)
        except Exception:  # noqa: BLE001
            logger.exception("Abruf oder Zusammenfassung fehlgeschlagen")
            summary = (
                "Der Abruf der Messenger-Nachrichten ist aktuell nicht verfuegbar. "
                "Bitte versuche es spaeter erneut."
            )
            twiml = voice_service.incoming_response(
                summary=summary,
                has_messages=False,
                action_url=followup_url,
            )
            return PlainTextResponse(content=twiml, media_type="application/xml")

        store.save_call_context(call_sid, summary, unread_messages)
        store.mark_messages_read([msg.id for msg in unread_messages])

        twiml = voice_service.incoming_response(
            summary=summary,
            has_messages=bool(unread_messages),
            action_url=followup_url,
        )
        return PlainTextResponse(content=twiml, media_type="application/xml")

    @app.post("/twilio/voice/followup")
    async def twilio_voice_followup(request: Request) -> Response:
        form = await request.form()
        if not validate_twilio_signature(request, form, app_settings):
            logger.warning("Twilio-Signaturpruefung fehlgeschlagen (followup).")
            return Response(status_code=403)

        call_sid = str(form.get("CallSid", "unknown-call"))
        speech_result = str(form.get("SpeechResult", "")).strip()
        followup_url = build_public_url(request, app_settings, "/twilio/voice/followup")

        if not speech_result:
            twiml = voice_service.followup_response(
                answer="Ich habe dich nicht verstanden. Bitte formuliere die Frage noch einmal.",
                action_url=followup_url,
            )
            return PlainTextResponse(content=twiml, media_type="application/xml")

        if voice_service.should_end(speech_result):
            return PlainTextResponse(
                content=voice_service.goodbye_response(),
                media_type="application/xml",
            )

        context = store.get_call_context(call_sid)
        if context is None:
            twiml = voice_service.followup_response(
                answer="Fuer diesen Anruf liegt kein Kontext vor. Starte bitte einen neuen Anruf.",
                action_url=followup_url,
            )
            return PlainTextResponse(content=twiml, media_type="application/xml")

        if len(context.conversation) >= app_settings.max_followup_turns * 2:
            return PlainTextResponse(
                content=voice_service.goodbye_response(
                    text="Wir haben die maximale Anzahl an Rueckfragen erreicht. Auf Wiederhoeren."
                ),
                media_type="application/xml",
            )

        updated_conversation = store.append_conversation_turn(call_sid, role="caller", text=speech_result)

        answer = await llm_service.answer_followup(
            question=speech_result,
            messages=context.messages,
            summary=context.summary,
            conversation=updated_conversation,
        )
        store.append_conversation_turn(call_sid, role="assistant", text=answer)

        twiml = voice_service.followup_response(
            answer=answer,
            action_url=followup_url,
        )
        return PlainTextResponse(content=twiml, media_type="application/xml")

    return app


app = create_app()
