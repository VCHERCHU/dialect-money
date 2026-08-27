"""The counter-metric, enforced in code.

From the problem statement:

    Counter-metric: percentage of published videos whose every factual claim
    traces to a cited whitelisted page. This must be 100%. A single confidently
    narrated wrong figure in Hokkien does more damage than the product does good.

Nobody on the team is going to eyeball Tai-lo for a dropped decimal point, so
this module does the mechanical half: every figure that appears in the English
script must survive both translation hops unchanged.

This checks figures, not meaning. It cannot tell you the Hokkien is faithful -
only that no number went missing or changed on the way. Human review of the
Mandarin remains the real safeguard; this catches the failure mode that human
review is worst at.
"""

import re

# Numbers with optional currency, thousands separators, decimals and percent.
FIGURE_RE = re.compile(
    r"""
    (?:S?\$|SGD\s*)?          # optional currency marker
    \d{1,3}(?:,\d{3})+        # 1,000 / 1,234,567
    (?:\.\d+)?
    |
    (?:S?\$|SGD\s*)?
    \d+(?:\.\d+)?             # 55 / 3.5
    \s*%?                     # optional percent
    """,
    re.VERBOSE,
)

# Han numerals, so a figure rewritten as 一千 is recognised rather than reported
# missing. Order matters: longest first.
HAN_DIGITS = {
    "零": "0", "〇": "0", "一": "1", "二": "2", "两": "2", "兩": "2",
    "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9",
}


def normalise(figure):
    """Reduce a figure to its comparable numeric core. Pure.

    "S$1,000" "$1000" and "1000" all become "1000"; "5 %" becomes "5%".
    """
    text = figure.strip().lower()
    text = re.sub(r"^(s\$|sgd\s*|\$)", "", text)
    text = text.replace(",", "").replace(" ", "")
    if text.endswith("%"):
        core = text[:-1]
        return f"{_trim_zeros(core)}%"
    return _trim_zeros(text)


def _trim_zeros(number):
    """3.50 -> 3.5, 3.0 -> 3, so formatting differences do not read as changes."""
    if "." not in number:
        return number
    trimmed = number.rstrip("0").rstrip(".")
    return trimmed or "0"


def extract_figures(text):
    """Every distinct figure in a piece of text, normalised. Pure."""
    found = set()
    for match in FIGURE_RE.findall(text):
        cleaned = normalise(match)
        # A bare "0" or empty match carries no factual weight.
        if cleaned and cleaned not in {"0", "0%"}:
            found.add(cleaned)
    return found


def han_to_arabic(text):
    """Rewrite simple Han numerals as digits so they can be compared. Pure.

    Deliberately simple: handles digit-by-digit and the common 十/百/千/万
    shapes well enough to avoid false alarms. Anything it misses is reported as
    a figure to check by hand, which is the safe direction to fail.
    """
    result = []
    for char in text:
        result.append(HAN_DIGITS.get(char, char))
    converted = "".join(result)

    # 1十 -> 10, 5百 -> 500, and so on.
    for han, zeros in (("十", 1), ("百", 2), ("千", 3), ("万", 4), ("萬", 4)):
        converted = re.sub(
            rf"(\d)\s*{han}", lambda m: m.group(1) + "0" * zeros, converted
        )
    return converted


def check(english, *translations):
    """Compare figures in the English script against each translation.

    Returns {"ok": bool, "expected": [...], "missing": {label: [...]}}.
    Each translation is a (label, text) pair.
    """
    expected = extract_figures(english)
    missing = {}

    for label, text in translations:
        if not text:
            missing[label] = sorted(expected)
            continue
        present = extract_figures(text) | extract_figures(han_to_arabic(text))
        gone = sorted(expected - present)
        if gone:
            missing[label] = gone

    return {
        "ok": not missing,
        "expected": sorted(expected),
        "missing": missing,
    }


def format_report(result):
    """Human-readable summary of a check() result. Pure."""
    if not result["expected"]:
        return "No figures in the English script - nothing to verify."

    count = len(result["expected"])
    if result["ok"]:
        return f"All {count} figure(s) survived both translations: {', '.join(result['expected'])}"

    lines = [f"FIGURE MISMATCH - {count} figure(s) in the English script:",
             f"  expected: {', '.join(result['expected'])}"]
    for label, gone in result["missing"].items():
        lines.append(f"  missing from {label}: {', '.join(gone)}")
    lines.append("  Do not publish until a human has checked these.")
    return "\n".join(lines)
