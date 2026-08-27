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
    OPENCODE_MODEL=glm-5.3-flash

TWO MODES
    POST /api/ask with {"stream": true} answers as newline-delimited JSON, one
    event per line, so the page can show and speak each line the moment it is
    complete. Without the flag it answers once with the whole object -- kept
    because it is far easier to curl.

    The line splitting lives here in both modes, so the browser never has to
    reimplement it and the two modes cannot disagree about what a line is.

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

# Models on this endpoint think before they answer, and spend tokens doing it:
# qwen3.7-plus used 889 completion tokens on a four-line answer. A small budget is
# consumed entirely by that, returning finish_reason="length" with an empty
# content string -- which looks exactly like a broken endpoint and is not.
#
# Streaming makes the shape of it visible: nothing arrives for many seconds, then
# every line lands within about a second. The wait is thinking, not transmission,
# so streaming is not what fixes her wait -- reading the retrieved explainer
# first is.
MAX_TOKENS = 1500
TIMEOUT = 120

REFUSAL = "NO_ANSWER"
MAX_LINES = 5
MAX_ASKS = 3

# Telling the questions apart from the answer is the fragile seam here, and
# getting it wrong is not cosmetic: an unrecognised separator turns her follow-up
# questions into spoken answer lines, or -- once the answer cap is full --
# silently drops them, which is how the most useful part of the product
# disappears without an error.
#
# The model is a .env knob and they do not agree on the separator. glm-5.3-flash
# alternates between "问：" and "ASK:" across runs and sometimes omits it
# entirely; kimi-k3 and qwen3.7-plus write "ASK:" reliably. So the prompt asks for
# a per-line prefix rather than a one-off separator line, and both shapes are
# accepted: a whole line that is only the marker, or a marker prefixing each
# question. Per-line prefixes also survive streaming, where a line already
# emitted cannot be reclassified after the fact.
ASK_MARKER = re.compile(r"^\s*(ASK|问|问题)\s*[:：]\s*$", re.IGNORECASE)
ASK_PREFIX = re.compile(r"^\s*(ASK|问|问题)\s*[:：]\s*(?=\S)", re.IGNORECASE)

SYSTEM = """You answer money questions for a Singaporean senior in her 70s. She speaks {dialect} and reads very little English. Someone is often trying to sell her something.

RULES
1. Answer ONLY from the SOURCE MATERIAL below. If it does not cover her question, reply with exactly: {refusal}
2. Never recommend a product, never tell her what to buy, never say whether something is worth it. Explain what is being sold to her so she can judge.
3. Never state a figure, rate, percentage or scheme name that is not in the source material. If she asks for a number that is not there, say you do not have it.
4. Reply in simple Chinese. Short sentences, one idea per line, at most 5 lines. No greetings, no sign-off, no markdown.
5. Then up to 3 questions she can put to the salesperson. Put each question on its own line and begin every one of those lines with 问: -- including the first. Do not write a heading, and do not number them.

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


def open_upstream(question, dialect, passages, stream):
    """Return the open upstream response. Caller closes it."""
    key = os.environ.get("OPENCODE_API_KEY")
    base = os.environ.get("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1")
    model = os.environ.get("OPENCODE_MODEL", "glm-5.3-flash")
    if not key:
        raise RuntimeError("OPENCODE_API_KEY is not set -- copy .env.example to .env")

    body = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.2,
        "stream": bool(stream),
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
            "Accept": "text/event-stream" if stream else "application/json",
            # Cloudflare in front of the endpoint answers 403 "error code: 1010"
            # to urllib's default User-Agent. Any ordinary UA passes.
            "User-Agent": "dialect-money/0.1 (+https://github.com/VCHERCHU/dialect-money)",
        },
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=TIMEOUT), model


def clean_line(raw):
    """Strip list markers the model sometimes adds despite being told not to."""
    return raw.strip().lstrip("-*0123456789.、) ").strip()


class LineSplitter:
    """Turns a stream of content deltas into answer lines and ASK questions.

    Used by both modes so they cannot disagree about what a line is.
    """

    def __init__(self):
        self.pending = ""
        self.in_asks = False
        self.refused = False
        self.lines = []
        self.asks = []

    def feed(self, piece):
        """Yield ('line'|'ask', text) for every line completed by this piece."""
        if self.refused:
            return
        self.pending += piece
        while "\n" in self.pending:
            raw, self.pending = self.pending.split("\n", 1)
            for event in self._take(raw):
                yield event

    def finish(self):
        """Yield anything left in the buffer at end of stream."""
        rest, self.pending = self.pending, ""
        for event in self._take(rest):
            yield event

    def _take(self, raw):
        if self.refused:
            return
        if REFUSAL in raw:
            self.refused = True
            return
        if ASK_MARKER.match(raw):
            self.in_asks = True
            return
        # A per-line prefix classifies that line on its own, whether or not a
        # separator ever arrived.
        prefixed = ASK_PREFIX.match(raw)
        if prefixed:
            self.in_asks = True
            raw = raw[prefixed.end():]
        line = clean_line(raw)
        if not line:
            return
        if self.in_asks:
            if len(self.asks) < MAX_ASKS:
                self.asks.append(line)
                yield ("ask", line)
        else:
            if len(self.lines) < MAX_LINES:
                self.lines.append(line)
                yield ("line", line)


def iter_content_deltas(resp):
    """Yield content deltas from an SSE stream, dropping reasoning deltas.

    reasoning_content is the model thinking aloud. It must never be shown to
    her or spoken, and on a reasoning model it is most of the stream.
    """
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            if data == "[DONE]":
                return
            continue
        try:
            chunk = json.loads(data)
        except ValueError:
            continue
        choice = (chunk.get("choices") or [{}])[0]
        piece = (choice.get("delta") or {}).get("content")
        if piece:
            yield piece


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
            stream = bool(data.get("stream"))
            if not question:
                raise ValueError("question is required")
            if not isinstance(passages, list) or not passages:
                raise ValueError("context is required -- nothing was retrieved")
        except Exception as exc:
            self.reply(400, {"error": str(exc)})
            return

        if stream:
            self.stream_answer(question, dialect, passages)
        else:
            self.whole_answer(question, dialect, passages)

    # ---- streaming ------------------------------------------------------
    def stream_answer(self, question, dialect, passages):
        try:
            resp, model = open_upstream(question, dialect, passages, stream=True)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            self.reply(502, {"error": "LLM {}: {}".format(exc.code, detail)})
            return
        except Exception as exc:
            self.reply(502, {"error": "{}: {}".format(type(exc).__name__, exc)})
            return

        # No Content-Length: the browser reads to EOF. protocol_version stays
        # HTTP/1.0, so returning from this handler closes the connection and
        # terminates the stream cleanly without chunked framing.
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        splitter = LineSplitter()
        try:
            with resp:
                self.emit({"type": "open", "model": model})
                for piece in iter_content_deltas(resp):
                    for kind, text in splitter.feed(piece):
                        self.emit({"type": kind, "text": text})
                for kind, text in splitter.finish():
                    self.emit({"type": kind, "text": text})
        except Exception as exc:
            # Whatever already reached her stays on screen; the page decides
            # whether it has enough to keep.
            self.emit({"type": "error", "error": "{}: {}".format(type(exc).__name__, exc)})
            return

        self.emit({
            "type": "done",
            "refused": splitter.refused or not splitter.lines,
            "lines": splitter.lines,
            "ask": splitter.asks,
            "model": model,
        })

    def emit(self, obj):
        try:
            self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            raise

    # ---- one-shot -------------------------------------------------------
    def whole_answer(self, question, dialect, passages):
        try:
            resp, model = open_upstream(question, dialect, passages, stream=False)
            with resp:
                payload = json.load(resp)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            self.reply(502, {"error": "LLM {}: {}".format(exc.code, detail)})
            return
        except Exception as exc:
            self.reply(502, {"error": "{}: {}".format(type(exc).__name__, exc)})
            return

        choice = (payload.get("choices") or [{}])[0]
        # Read content only. reasoning_content is the model thinking aloud.
        text = ((choice.get("message") or {}).get("content") or "").strip()

        splitter = LineSplitter()
        for _ in splitter.feed(text):
            pass
        for _ in splitter.finish():
            pass

        self.reply(200, {
            "refused": splitter.refused or not splitter.lines,
            "lines": splitter.lines,
            "ask": splitter.asks,
            "model": model,
            "finish_reason": choice.get("finish_reason"),
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
        port, os.environ.get("OPENCODE_MODEL", "glm-5.3-flash")))
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    main()
