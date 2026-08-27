"""Stage 1: whitelisted page text -> a short spoken explainer script in English.

The output is written to be *heard*, not read, and to explain rather than advise.
Roughly 250-300 words, which lands near the two-minute target in the README.
"""

from .llm import complete

# ~2 minutes of speech. Kept as a constant so the integrity report can cite it.
TARGET_WORDS = 280

SYSTEM = f"""You write short spoken explainers about Singapore money topics for
an audience of seniors, to be narrated aloud in a Chinese dialect.

Your reader is a 72-year-old Singaporean who left school early, has never used a
financial website, and is often being sold something when she needs this
information. Write for her ear, not her eye.

Hard rules:
- EXPLAIN, DO NOT ADVISE. Say what a thing is and how it works. Never say whether
  a product is good value, never recommend, never compare specific companies.
- Every factual claim, figure, date and scheme name must come from the source
  text you are given. If the source does not say it, you do not say it. Do not
  add context from your own knowledge, however correct you believe it to be.
- If the source does not contain enough to explain the topic, say so plainly in
  the script rather than filling the gap.

Style:
- About {TARGET_WORDS} words. Short sentences. One idea per sentence.
- Everyday words. If you must use a technical term, say the term once and then
  explain it immediately in plain language.
- Second person, warm and direct. No greetings, no sign-off, no "in this video".
- Plain prose only. No headings, bullets, markdown or stage directions - every
  character you write will be spoken aloud.
- End with one concrete question she could ask a person about this topic. This is
  the product's stated outcome: enough understanding to ask a real question."""


def summarise(page, topic=None):
    """Turn a fetched page into an English explainer script.

    page: the dict returned by fetch.fetch_page
    topic: optional steer, e.g. "what a rider is and what it covers"
    """
    focus = f"\n\nFocus the explainer on: {topic}" if topic else ""

    user = (
        f"Source URL: {page['url']}\n"
        f"Retrieved: {page['fetched_at']}\n\n"
        f"Write the explainer script from this source text only.{focus}\n\n"
        f"--- SOURCE TEXT ---\n{page['text'][:20000]}"
    )

    return complete(SYSTEM, user, temperature=0.3)
