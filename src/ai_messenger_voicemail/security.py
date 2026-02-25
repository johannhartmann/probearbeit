from fastapi import Request
from starlette.datastructures import FormData
from twilio.request_validator import RequestValidator

from ai_messenger_voicemail.config import Settings


def resolve_public_base_url(request: Request, settings: Settings) -> str:
    if settings.base_url:
        return settings.base_url.rstrip("/")

    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{scheme}://{host}"


def build_public_url(request: Request, settings: Settings, path: str | None = None) -> str:
    base = resolve_public_base_url(request, settings)
    target_path = path or request.url.path
    if not target_path.startswith("/"):
        target_path = f"/{target_path}"

    query_string = request.url.query if path is None else ""
    if query_string:
        return f"{base}{target_path}?{query_string}"
    return f"{base}{target_path}"


def validate_twilio_signature(request: Request, form: FormData, settings: Settings) -> bool:
    if not settings.twilio_validate_signature:
        return True
    if not settings.twilio_auth_token:
        return False

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False

    validator = RequestValidator(settings.twilio_auth_token)
    target_url = build_public_url(request, settings)
    params: dict[str, str] = {}
    for key in form.keys():
        value = form.get(key)
        if value is None:
            continue
        params[str(key)] = str(value)

    return validator.validate(target_url, params, signature)
