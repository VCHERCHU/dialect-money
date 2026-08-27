# Design source

The screens behind the prototype, as editable source rather than flattened images.

Each `.dc.html` is one artboard; `canvas.json` places them and splits them across two
pages. They are assembled into a single browsable canvas by Claude Design — the
assembled file is ~2 MB of editor code and is deliberately **not** committed
(see `.gitignore`).

| File | What it is |
| --- | --- |
| `Main.dc.html` | The chosen direction, built out — the inbox home screen |
| `SentEmpty.dc.html` | Its empty state, which is where this direction fails if it fails |
| `Ask.dc.html` | `ask.html` idle — the mic, and the type-or-tap way in |
| `AskAnswer.dc.html` | Listening, heard, and the two-pass answer with its citation |
| `AskRefuse.dc.html` | The refusal — the counter-metric made visible |
| `VideoTitle.dc.html` | Video mode, wordless — a drawn situation instead of a title |
| `VideoPlaying.dc.html` | Talking: moving bars instead of a status label |
| `VideoPaused.dc.html` | Stopped: the bars fall flat and turn amber |
| `VideoEnd.dc.html` | The ask, drawn as an act — her, a question, an arrow, him |
| `VideoIcons.dc.html` | The wordless vocabulary: six situations, the controls, three sound states |
| `ProductThinking.dc.html` | The 4Cs, Five Whys and outcome metrics the design is judged on |
| `AppIcon.dc.html` | The mark at true 180/120/87/60/40px, plus round, dark, one-colour and greyscale |
| `Logo.dc.html` | Horizontal, stacked and reversed lockups, and the smallest usable size |
| `OptionA.dc.html` · `OptionB.dc.html` · `OptionC.dc.html` | The three directions reviewed; C was chosen |

## `identity/` — a second canvas

[`identity/`](identity/) holds a separate canvas for the 话 mark: the logo, app
icon, usage rules, the three directions that lost, and `make-assets.py` with the
exported favicons and SVGs it produces.

It sits in its own folder because a `canvas.json` is the manifest for one folder,
and both canvases name a `Main.dc.html` and an `AppIcon.dc.html`. Merging them
into one manifest would have meant renaming somebody's artboards; a folder each
costs nothing and keeps both openable as their authors laid them out.

Colours and type are lifted from `site/index.html`, `site/video.html` and `site/ask.html`
rather than invented — `#0b5c46`, `#fbf9f4`, `#1a1a17`, the dark stage's `#14140f` / `#6fd3ad`,
14px radii, and the same CJK font stack. Ask's listening state uses `ask.html`'s own
`--stop: #9b2c1f`.

One deliberate deviation: the microphone is drawn as SVG where `ask.html` uses the 🎤
emoji glyph. An emoji renders differently on every platform and cannot be recoloured
for the listening state. The same reasoning applies to the tortoise on the slow control.

The `Video*` boards remove all fourteen written labels from `site/video.html`'s chrome. Three
things stay as words on purpose: the spoken lines and the three questions (they are the
outcome, not decoration), and the dialect name — the one label she reliably reads, and no
picture tells Hokkien from Teochew.

Two things in here are not real data: the `女儿` / `义工` senders stand in for a
sender identity the product does not have yet, and the fifth "why" on the
product-thinking board is a synthesis of assumption 1, not a quote from
[PROBLEM-STATEMENT.md](../PROBLEM-STATEMENT.md).
