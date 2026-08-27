"""Minimal OpenAI-compatible chat client.

No SDK, no runtime dependencies — same constraint the lunchUncle Worker keeps.
Secrets come from the environment only.
"""

import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://opencode.ai/zen/go/v1"
DEFAULT_MODEL = "kimi-k2.5"
TIMEOUT_S = 120


class LLMError(Exception):
    """Raised when the provider returns a non-2xx response."""


def _api_key():
    key = os.environ.get("OPENCODE_API_KEY", "").strip()
    if not key:
        raise LLMError(
            "OPENCODE_API_KEY is not set. Copy .env.example to .env, fill it in, "
            "and run through run.py (which loads .env)."
        )
    return key


def complete(system, user, temperature=0.2, model=None, base_url=None):
    """Send one system+user turn and return the assistant's text.

    Temperature defaults low: this pipeline is doing faithful translation of
    financial guidance, not creative writing.
    """
    base_url = base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)
    model = model or os.environ.get("LLM_MODEL", DEFAULT_MODEL)

    payload = json.dumps({
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "content-type": "application/json",
            "authorization": f"Bearer {_api_key()}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:500]
        raise LLMError(f"LLM returned {err.code}: {detail}") from err

    return body["choices"][0]["message"]["content"].strip()
