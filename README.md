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
3. **kimi-k3** answers from those passages only, under a system prompt that
   forbids any figure not in them, forbids recommending anything, and requires
   the literal token `NO_ANSWER` when they don't cover the question.
4. **Fallback** — any proxy failure reads the retrieved explainer verbatim
   instead, labelled *offline* in the UI. Always safe: that text is
   human-drafted.

```bash
cp .env.example .env      # then paste your OPENCODE_API_KEY
python server/app.py      # http://127.0.0.1:8766
```

The proxy exists for one reason: **the API key must never reach the browser.**
This site is public, so a key in client-side JS is a key anyone can read. Pages
cannot run the proxy, so the deployed page always uses the keyword fallback.

Rough edges worth knowing:

- **kimi-k3 is a reasoning model — 20 to 30 seconds per answer.** Far too slow
  for a 72-year-old holding a phone. The fix is probably to speak the retrieved
  explainer immediately and let the model refine, rather than making her wait in
  silence.
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
