# Dialect Money

Authoritative Singapore money guidance, turned into spoken Hokkien, Teochew and
Cantonese, for seniors who are locked out of it by English text on websites.

> **Dialect-only seniors are locked out of financial guidance that already
> exists — not because it is missing, but because it is written, in English, for
> someone else.**

**[Read the full problem statement →](PROBLEM-STATEMENT.md)**

---

## Where this stands

Problem definition, plus a clickable prototype live at
<https://vcherchu.github.io/dialect-money/>. Nothing should be built *for real*
until assumption 1 — distribution — has been tested against a real person.

## The prototype

Static site, no build step, no dependencies. Two files carry it:

| File | Role |
| --- | --- |
| `site/index.html` | The whole app — markup, styles and logic |
| `site/explainers.js` | Data only: dialects, the source whitelist, the explainer library |

```bash
python -m http.server 8766 --bind 127.0.0.1 --directory site
# open http://127.0.0.1:8766/index.html
```

What it demonstrates:

- **Audio-first.** Every card is a 60px play button. Tapping the card plays; the
  line being spoken is highlighted for whoever is reading along.
- **Dialect switch** — Hokkien, Teochew, Cantonese — remembered between visits.
  Cards with no narration yet show as `还在制作中`, so the publishing pipeline is
  visible rather than hidden.
- **"Questions you can ask them."** Each explainer ends with three questions Mdm
  Tan can put to the agent or teller. This is where the stated outcome —
  *confident enough to ask* — actually lives.
- **Share via WhatsApp**, because that is the only channel that plausibly reaches
  her. The deep link opens straight to that explainer.
- **Every card cites its source** and links to it.

What is honestly faked, and labelled as such in the UI:

- **The voice.** No real Hokkien or Teochew TTS exists behind this — playback
  borrows the browser's Mandarin or Cantonese voice. This is assumption 2 and the
  prototype does not resolve it.
- **The crawl.** `lastCrawl` and source deep links are static. Links land on each
  source's home page; a fabricated deep link would be worse.
- **The scripts.** Drafts, no specific rates or figures quoted, and not through
  the human accuracy check the problem statement requires.

## Deploy

Live at <https://vcherchu.github.io/dialect-money/>.

Pushing to `main` under `site/**` deploys it — that is the whole release
process. `.github/workflows/deploy-pages.yml` publishes `./site` as the site
root, so a README-only commit produces no deploy run. That is expected, not a
broken pipeline.

Only `main` deploys. Work on a branch, merge, and the deploy follows.

```bash
gh run list --repo VCHERCHU/dialect-money --workflow deploy-pages.yml --limit 1
```

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
