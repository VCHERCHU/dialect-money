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

## The chat assistant

`site/ask.html` plus `server/app.py`. She asks out loud; the answer comes back
spoken, cited, or refused. This is the strand the project owner is building; a
teammate owns video generation, and another owns MERaLiON for Chinese-to-Hokkien.

How an answer is produced:

1. **Retrieval** — keyword scoring over the explainer corpus picks up to three
   passages. This decides everything the model is allowed to see.
2. **Refusal before the model** — nothing retrieved means no permitted context,
   so it says "I don't know" without spending a call. This closes the only door
   an unsourced answer could arrive through.
3. **Speak first.** The retrieved explainer is read out immediately, in under a
   second. It is already human-drafted and sourced, so there is no reason to make
   her wait for a model to approve it.
4. **glm-5.3-flash refines, streaming.** It answers from those passages only, under a
   system prompt that forbids any figure not in them, forbids recommending
   anything, and requires the literal token `NO_ANSWER` when they don't cover the
   question. The proxy streams newline-delimited JSON, one event per line, and
   splits lines itself so the page never reimplements that. Each line appears —
   and is spoken — as it lands. Refinement is an improvement, never a gate: if she
   is still mid-sentence on the verbatim read, the audio is not swapped under her
   and a button offers the clearer version instead.
5. **Fallback** — any proxy failure keeps the verbatim explainer, labelled
   *offline* in the UI. Always safe: that text is human-drafted.

```bash
cp .env.example .env      # then paste your OPENCODE_API_KEY
python server/app.py      # http://127.0.0.1:8766
```

The proxy exists for one reason: **the API key must never reach the browser.**
This site is public, so a key in client-side JS is a key anyone can read. Pages
cannot run the proxy, so the deployed page always uses the keyword fallback.

Rough edges worth knowing:

- **Streaming did not fix the wait, and was never going to.** Every model here
  thinks for seconds and then emits the whole answer inside about one. Streamed on
  the same rider question: `kimi-k3` first line at 20.0s, done 21.9s;
  `glm-5.3-flash` first line at 10.2s, done 11.6s. Streaming buys a second or two
  of a ten-to-twenty-second wait. **Reading the explainer first is what actually
  removes her wait.** Keep both, but do not mistake which one is load-bearing.
- **Model choice moves the number more than streaming does.** Same prompt,
  one-shot, measured on this endpoint:

  | Model | Time | Notes |
  | --- | --- | --- |
  | `glm-5.3-flash` | 13.4s | **current default** — fastest measured |
  | `deepseek-v4-flash` | 14.7s | |
  | `qwen3.7-plus` | 17.0s | most consistent separator |
  | `kimi-k3` | 20.4s | |

  Swap with `OPENCODE_MODEL` in `.env`.
- **Telling the questions apart from the answer is the fragile seam.** Asking for
  one `ASK:` separator line was not robust: `glm-5.3-flash` alternates between
  `问：` and `ASK:` between runs and sometimes omits it, and one observed run
  produced an answer with the questions silently swallowed by the five-line cap —
  no error, just the most valuable part of the product missing. The prompt now
  asks for a `问:` prefix on *every* question line, and the parser accepts either
  shape. Per-line prefixes also survive streaming, where a line already spoken
  cannot be reclassified after the fact. Verified 3/3 runs on `glm-5.3-flash`, in
  both streaming and one-shot mode.
- **The spoken line and the highlighted line can diverge.** When refined text
  replaces verbatim text under live speech, the words being spoken no longer match
  what is on screen, so line highlighting switches off rather than pointing at the
  wrong line.
- **Retrieval runs in the browser** and the client posts the passages it wants
  answered from. Fine locally, wrong in production — a client could post any
  context and have it read back in a trusted voice.
- **Cloudflare rejects urllib's default User-Agent** with `403 error code: 1010`.
  The proxy sends an ordinary one.
- Speech in and out are still browser Mandarin/Cantonese stand-ins. No browser
  recognises or speaks Hokkien; that is the MERaLiON dependency.

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
