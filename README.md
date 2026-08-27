# Dialect Money

Authoritative Singapore money guidance, turned into spoken Hokkien, Teochew and
Cantonese, for seniors who are locked out of it by English text on websites.

> **Dialect-only seniors are locked out of financial guidance that already
> exists — not because it is missing, but because it is written, in English, for
> someone else.**

**[Read the full problem statement →](PROBLEM-STATEMENT.md)**

---

## Where this stands

Problem definition, plus a clickable prototype on the `develop` branch. Nothing
should be built *for real* until assumption 1 — distribution — has been tested
against a real person.

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
