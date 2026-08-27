# Dialect Money

Authoritative Singapore money guidance, turned into spoken Hokkien, Teochew and
Cantonese, for seniors who are locked out of it by English text on websites.

> **Dialect-only seniors are locked out of financial guidance that already
> exists — not because it is missing, but because it is written, in English, for
> someone else.**

**[Read the full problem statement →](PROBLEM-STATEMENT.md)**

---

## Where this stands

Problem definition. Nothing has been built, and nothing should be built until
assumption 1 — distribution — has been tested against a real person.

## The shape of the idea

A site that crawls **whitelisted sources only** (CPF, MAS, MoneySense, IRAS, MOF,
gov.sg), drafts short explainers, narrates them in dialect, and auto-publishes
them to a browsable library. No login, no generate button, every video citing the
page it came from.

v1 answers *"help me understand what is being sold to me"* — it explains, it does
not advise.

## Next step

Generate one two-minute Hokkien explainer from a single MoneySense page and play
it to two or three seniors. That one artefact tests distribution, voice quality
and format at once.

---

Coursework for Product Thinking, Institute of Digital Government.

---

## Pipeline (work in progress)

A first pass at the build described above: crawl one whitelisted page, summarise
it, translate it into Hokkien, and narrate it.

```
EN summary ──▶ Mandarin ──▶ Hokkien (漢字 + Tâi-lô) ──▶ audio
                   │                                      │
        human-checkable review              MERaLiON, Singapore Hokkien
```

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # add your LLM key
.venv/bin/python run.py https://www.moneysense.gov.sg/<page> --tts hokkien
```

Every stage writes its own file to `out/`, so each can be reviewed alone. The
Mandarin file matters most: it is the one a literate reviewer can actually check
before anything is spoken aloud.

### Why Mandarin in the middle

Models are much stronger English→Mandarin than English→Hokkien, and the Mandarin
version is a checkpoint a human can read. Two hops do compound error, so
`pipeline/integrity.py` re-checks every figure from the English script against
both translations and refuses to pass if one went missing. That is the
100%-traceability counter-metric, enforced mechanically.

### Narration

`--tts script` writes a Han + Tâi-lô script for a **human** Hokkien speaker.
`--tts hokkien` uses [MERaLiON-OmniVoice-Hokkien-TTS](https://huggingface.co/MERaLiON/MERaLiON-OmniVoice-Hokkien-TTS),
A*STAR's **Singapore** Hokkien model — not Taiwanese, so no Quanzhou/Zhangzhou
accent mismatch. It runs locally on CPU: no API key, no per-character cost,
nothing leaving the machine. Its licence is the MERaLiON-3 Public Licence, not a
standard OSS licence — read it before publishing beyond coursework.

Apple Silicon note: this model hard-crashes (SIGBUS) on MPS at both float16 and
float32. CPU float32 works; ~11s for a first clip, ~5s once warm.

### MCP server

`mcp_server.py` exposes the Hokkien voice as MCP tools (`speak_hokkien`,
`hokkien_status`), so it is callable from Claude Code or any MCP client. Because
the server is long-lived it keeps the model in memory between calls, which is
where the cold/warm difference above comes from.

```sh
claude mcp add hokkien-tts -- "$PWD/.venv/bin/python" "$PWD/mcp_server.py"
```

**Input must be Hokkien in Han characters, not Mandarin.** Mandarin does not
error — it produces a literary reading (讀書音): real Hokkien phonology wrapped
around Mandarin vocabulary, which sounds like a broadcast rather than a person.
