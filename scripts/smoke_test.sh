#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

printf "[smoke] healthz\n"
curl -fsS "${BASE_URL}/healthz" | python3 -m json.tool

printf "[smoke] readyz\n"
curl -fsS "${BASE_URL}/readyz" | python3 -m json.tool

printf "[smoke] telegram sync\n"
curl -fsS -X POST "${BASE_URL}/telegram/sync" | python3 -m json.tool

printf "[smoke] twilio incoming\n"
curl -fsS -X POST "${BASE_URL}/twilio/voice/incoming" \
  -d "CallSid=smoke-call-1" \
  | sed -n '1,8p'
