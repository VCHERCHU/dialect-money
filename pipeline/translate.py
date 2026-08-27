"""Stage 2 and 3: English -> Mandarin -> Hokkien.

Why go through Mandarin at all, rather than English straight to Hokkien?

1. It is a reviewable checkpoint. Almost nobody on a project like this reads
   Tai-lo, but plenty read Chinese. The Mandarin version is the artefact a human
   can actually check before anything is narrated, which is what protects the
   100%-traceability counter-metric in the problem statement.
2. Models are markedly stronger on English->Mandarin than English->Hokkien.

The cost is that two hops compound error, which is why integrity.py re-checks
every figure against the English source afterwards.

The trap in the second hop is register. Written Mandarin is not written Hokkien:
different vocabulary and grammar, not merely different pronunciation. Feeding
formal Mandarin to a Hokkien voice yields literary reading (讀書音) - real
Hokkien sounds, but stilted and broadcast-like. Colloquial Hokkien (白話) is what
an actual person speaks. The prompt below pushes hard on this, and it is the
first thing to check if a sample sounds wrong to a native speaker.
"""

import json

from .llm import complete

MANDARIN_SYSTEM = """You translate short spoken scripts from English into
Chinese, for narration to elderly Singaporeans.

- Use Simplified Chinese, as used in Singapore.
- Translate for the ear. Spoken register, short sentences, everyday words. Not
  written or literary Chinese.
- Preserve every number, percentage, currency amount, date, age and scheme name
  exactly. Do not round, convert, localise or reformat any figure.
- Keep the meaning strictly. Do not add explanation, soften, or omit anything.
- Output only the translated script. No notes, no pinyin, no commentary."""

HOKKIEN_SYSTEM = """You translate spoken Chinese scripts into Hokkien (Minnan)
as actually spoken by elderly Chinese Singaporeans.

This is the critical instruction: produce COLLOQUIAL SPOKEN HOKKIEN (白話), not a
Hokkien literary reading (讀書音) of Mandarin words. Do not simply map Mandarin
characters onto Hokkien pronunciations. Where colloquial Hokkien uses a
different word from Mandarin, use the Hokkien word. Some examples of the
distinction you must apply throughout: 什麼 -> 啥物 (siann2-mih8), 現在 ->
這馬 (tsit-ma2), 我們 -> 阮 (guan2) or 咱 (lan2), 錢 -> 錢 (tsinn5), 給 ->
予 (hoo7), 不是 -> 毋是 (m7-si7).

Aim at Singapore Hokkien, which leans towards Quanzhou pronunciation rather than
the Zhangzhou-leaning Taiwanese variety, and avoid Japanese-derived loanwords
common in Taiwanese Hokkien but not used in Singapore.

Preserve every number, percentage, currency amount, date, age and scheme name
exactly as given. Financial figures must survive translation untouched.

Return a single JSON object and nothing else:
{
  "han": "the script in Han characters, Hokkien colloquial orthography",
  "tailo": "the same script in Tai-lo romanisation, with tone numbers",
  "register_notes": "one or two sentences on any place you had to choose between
                     a colloquial and a literary form, for a reviewer to check"
}"""


def to_mandarin(english_script):
    """Stage 2: English explainer -> spoken Simplified Chinese."""
    return complete(MANDARIN_SYSTEM, english_script, temperature=0.2)


def to_hokkien(mandarin_script):
    """Stage 3: Mandarin -> Hokkien, returned as {han, tailo, register_notes}.

    Falls back to treating the whole reply as Han text if the model does not
    return usable JSON, so a formatting wobble never loses a translation.
    """
    raw = complete(HOKKIEN_SYSTEM, mandarin_script, temperature=0.2)
    return parse_hokkien(raw)


def parse_hokkien(raw):
    """Pull {han, tailo, register_notes} out of a model reply. Pure."""
    text = raw.strip()

    # Models often wrap JSON in a fenced code block.
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if len(lines) > 2 else lines).strip()
        if text.startswith("json"):
            text = text[4:].strip()

    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return {"han": raw.strip(), "tailo": "", "register_notes": "",
                "parse_failed": True}

    return {
        "han": (data.get("han") or "").strip(),
        "tailo": (data.get("tailo") or "").strip(),
        "register_notes": (data.get("register_notes") or "").strip(),
        "parse_failed": False,
    }
