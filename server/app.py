"""Local dev server for the Dialect Money chat assistant.

Serves site/ and proxies one endpoint, POST /api/ask, to the LLM. The point of
the proxy is that the API key stays here and never reaches the browser: the
deployed site is public, and a key in client-side JS is a key anyone can read.

Standard library only -- no pip install, matching the repo's no-dependencies
promise.

    python server/app.py            # http://127.0.0.1:8766

Config comes from .env in the repo root (gitignored):

    OPENCODE_API_KEY=sk-...
    OPENCODE_BASE_URL=https://opencode.ai/zen/go/v1
    OPENCODE_MODEL=kimi-k3

WHERE THIS PROTOTYPE IS LOOSE
    Retrieval happens in the browser and the client posts the passages it wants
    answered from. That is fine locally and wrong in production -- a client
    could post any context it liked and get it read back in a trusted voice.
    Moving retrieval behind this endpoint is the first hardening step, and it
    needs the corpus as real JSON rather than a JS object literal.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# kimi-k3 is a reasoning model: it spends tokens on reasoning_content before it
# writes any answer. A small budget returns finish_reason="length" and an empty
# content string, which looks like a broken endpoint but is not.
MAX_TOKENS = 1500
TIMEOUT = 90

REFUSAL = "NO_ANSWER"

SYSTEM = """You answer money questions for a Singaporean senior in her 70s. She speaks {dialect} and reads very little English. Someone is often trying to sell her something.

RULES
1. Answer ONLY from the SOURCE MATERIAL below. If it does not cover her question, reply with exactly: {refusal}
2. Never recommend a product, never tell her what to buy, never say whether something is worth it. Explain what is being sold to her so she can judge.
3. Never state a figure, rate, percentage or scheme name that is not in the source material. If she asks for a number that is not there, say you do not have it.
4. Reply in simple Chinese. Short sentences, one idea per line, at most 5 lines. No greetings, no sign-off, no markdown.
5. Then a line containing only ASK: followed by up to 3 questions she can put to the salesperson, one per line.

SOURCE MATERIAL
{context}"""


def load_env(path):
    """Minimal .env reader. Real values already in the environment win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def build_context(passages):
    """Flatten the retrieved passages into the only material the model may use."""
    blocks = []
    for p in passages[:3]:
        source = str(p.get("source", "unknown source"))[:200]
        title = str(p.get("title", ""))[:300]
        lines = [str(x)[:500] for x in (p.get("lines") or [])][:12]
        blocks.append("({})\n{}\n{}".format(source, title, "\n".join(lines)))
    return "\n\n".join(blocks)


def call_llm(question, dialect, passages):
    key = os.environ.get("OPENCODE_API_KEY")
    base = os.environ.get("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1")
    model = os.environ.get("OPENCODE_MODEL", "kimi-k3")
    if not key:
        raise RuntimeError("OPENCODE_API_KEY is not set -- copy .env.example to .env")

    body = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM.format(
                    dialect=dialect,
                    refusal=REFUSAL,
                    context=build_context(passages),
                ),
            },
            {"role": "user", "content": question},
        ],
    }

    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            # Cloudflare in front of the endpoint answers 403 "error code: 1010"
            # to urllib's default User-Agent. Any ordinary UA passes.
            "User-Agent": "dialect-money/0.1 (+https://github.com/VCHERCHU/dialect-money)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        payload = json.load(resp)

    choice = (payload.get("choices") or [{}])[0]
    # Read content only. reasoning_content is the model thinking aloud and must
    # never be shown to her or spoken.
    text = (choice.get("message") or {}).get("content") or ""
    return text.strip(), model, choice.get("finish_reason")


def split_answer(text):
    """Separate the spoken answer from the questions she can ask."""
    if REFUSAL in text:
        return [], [], True

    parts = re.split(r"^\s*ASK\s*[:：]\s*$", text, maxsplit=1, flags=re.MULTILINE)
    body = parts[0]
    tail = parts[1] if len(parts) > 1 else ""

    def clean(block):
        out = []
        for raw in block.splitlines():
            line = raw.strip().lstrip("-*0123456789.、) ").strip()
            if line:
                out.append(line)
        return out

    lines = clean(body)[:5]
    asks = clean(tail)[:3]
    if not lines:
        return [], [], True
    return lines, asks, False


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") != "/api/ask":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 64_000:
                raise ValueError("request too large")
            data = json.loads(self.rfile.read(length) or b"{}")
            question = str(data.get("question") or "").strip()[:500]
            dialect = str(data.get("dialect") or "Hokkien")[:40]
            passages = data.get("context") or []
            if not question:
                raise ValueError("question is required")
            if not isinstance(passages, list) or not passages:
                raise ValueError("context is required -- nothing was retrieved")
        except Exception as exc:
            self.reply(400, {"error": str(exc)})
            return

        try:
            text, model, finish = call_llm(question, dialect, passages)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            self.reply(502, {"error": "LLM {}: {}".format(exc.code, detail)})
            return
        except Exception as exc:
            self.reply(502, {"error": "{}: {}".format(type(exc).__name__, exc)})
            return

        lines, asks, refused = split_answer(text)
        self.reply(200, {
            "refused": refused,
            "lines": lines,
            "ask": asks,
            "model": model,
            "finish_reason": finish,
        })

    def reply(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def main():
    load_env(ROOT / ".env")
    port = int(os.environ.get("PORT", "8766"))
    if not os.environ.get("OPENCODE_API_KEY"):
        print("WARNING: OPENCODE_API_KEY not set. /api/ask will return 502 and the\n"
              "         page will fall back to keyword retrieval.", file=sys.stderr)
    handler = partial(Handler, directory=str(SITE))
    print("Dialect Money on http://127.0.0.1:{}  (model {})".format(
        port, os.environ.get("OPENCODE_MODEL", "kimi-k3")))
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    main()
