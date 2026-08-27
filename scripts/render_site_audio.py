#!/usr/bin/env python3
"""Render the site's Hokkien narration with MERaLiON.

    python3 scripts/render_site_audio.py --dry-run
    python3 scripts/render_site_audio.py
    python3 scripts/render_site_audio.py --only ip-rider

Reads `hokkien.script` for every explainer in site/explainers.js and writes one
clip per line to site/audio/<id>.hokkien.<line>.mp3 — the exact paths
site/index.html asks for. One clip per line rather than one per explainer,
because the app highlights the line being read, and because a short generation
is where this model is strongest.

Commit the .mp3 files: GitHub Pages serves them as static assets. If they are
absent the app falls back to the browser voice, so the site is never broken by
not having run this.

Needs the Hokkien TTS extras. No ffmpeg: libsndfile 1.2 writes MP3 itself,
and say_hokkien picks the format from the output file's extension.

    .venv/bin/pip install -r requirements.txt
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA = ROOT / "site" / "explainers.js"
AUDIO_DIR = ROOT / "site" / "audio"
DIALECT = "hokkien"

# Narration speed. Below 1.0 is slower, which suits an elderly listener.
SPEED = 0.9

# --------------------------------------------------------------------------
# Reading the data file
#
# explainers.js is JavaScript, not JSON: single-quoted strings, bare keys, and
# comments. Rather than regex at it — one title contains double quotes, which a
# naive quote swap would corrupt — walk it once, string-aware, and emit JSON.
# --------------------------------------------------------------------------

def js_to_json(text):
    """Convert the JS object literal in explainers.js to JSON text."""
    out = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        # Comments, only ever outside a string here.
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i = text.find("\n", i)
            if i < 0:
                break
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue

        # A string literal in either quote style becomes a JSON string.
        if ch in "'\"":
            quote = ch
            i += 1
            buf = []
            while i < n and text[i] != quote:
                if text[i] == "\\" and i + 1 < n:
                    buf.append(text[i:i + 2])
                    i += 2
                    continue
                buf.append(text[i])
                i += 1
            i += 1  # closing quote
            raw = "".join(buf)
            # Re-escape for JSON: the content may hold " or \ of its own.
            body = raw.replace("\\'", "'").replace('"', '\\"')
            out.append('"' + body + '"')
            continue

        out.append(ch)
        i += 1

    body = "".join(out)

    # Trim `window.LIBRARY =` and the trailing semicolon.
    body = body[body.index("{"):body.rindex("}") + 1]

    # Quote bare keys, and drop trailing commas. Safe now: every string in the
    # text is double-quoted, and none of them contains an ASCII colon or a
    # `,}` / `,]` sequence.
    body = re.sub(r'([{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*)(\s*):', r'\1"\2"\3:', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    return body


def load_library():
    """Parse site/explainers.js into a dict."""
    text = DATA.read_text(encoding="utf-8")
    try:
        return json.loads(js_to_json(text))
    except ValueError as err:
        raise SystemExit(
            "Could not parse %s: %s\n"
            "The scanner in js_to_json() needs updating for whatever syntax "
            "was just added." % (DATA, err)
        )


def clips(library, only=None):
    """Yield (stem, line_index, han_text) for every clip to render.

    The shared closing line is yielded once, as `verify`, because it is
    identical in every explainer — six copies of the same audio would be
    six times the review surface for no gain.
    """
    verify = (library.get("verify") or {}).get(DIALECT) or {}
    if verify.get("script") and not only:
        state = "" if verify.get("checked") else "  (UNCHECKED draft)"
        print("  %-24s 1 line%s" % ("verify (shared)", state))
        yield "verify", None, verify["script"]

    for item in library["explainers"]:
        if only and item["id"] != only:
            continue
        hokkien = item.get("hokkien") or {}
        lines = hokkien.get("script") or []
        if not lines:
            print("  skip %-24s no hokkien.script" % item["id"])
            continue
        if not hokkien.get("checked"):
            print("  %-24s %d lines  (UNCHECKED draft)" % (item["id"], len(lines)))
        else:
            print("  %-24s %d lines" % (item["id"], len(lines)))
        for index, line in enumerate(lines):
            yield item["id"], index, line


def target(stem, index):
    """Path for a clip. index None means the shared closing line."""
    if index is None:
        return AUDIO_DIR / ("%s.%s.mp3" % (stem, DIALECT))
    return AUDIO_DIR / ("%s.%s.%d.mp3" % (stem, DIALECT, index))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="List what would be rendered and exit. No model load.")
    parser.add_argument("--only", help="Render a single explainer by id.")
    parser.add_argument("--force", action="store_true",
                        help="Re-render clips that already exist.")
    args = parser.parse_args(argv)

    library = load_library()
    print("Reading %s" % DATA.relative_to(ROOT))
    work = list(clips(library, args.only))

    if not work:
        raise SystemExit("Nothing to render." + (" No such id: %s" % args.only if args.only else ""))

    print("\n%d clip(s) total -> %s/" % (len(work), AUDIO_DIR.relative_to(ROOT)))

    if args.dry_run:
        for explainer_id, index, line in work:
            mark = "exists" if target(explainer_id, index).exists() else "  new "
            print("  [%s] %s" % (mark, target(explainer_id, index).name))
            print("           %s" % line)
        print("\nDry run — nothing written. Drop --dry-run to render.")
        return 0

    from pipeline import tts  # imported here so --dry-run needs no torch

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    written = skipped = 0

    for explainer_id, index, line in work:
        out = target(explainer_id, index)
        if out.exists() and not args.force:
            skipped += 1
            continue
        print("  %s" % out.name, flush=True)
        try:
            # say_hokkien hands the path straight to soundfile, which picks the
            # format from the extension — libsndfile 1.2 encodes MP3 itself, so
            # there is no temp wav and no ffmpeg in the loop.
            result = tts.say_hokkien(line, str(out), speed=SPEED)
        except tts.TTSError as err:
            raise SystemExit("Narration failed on %s: %s" % (out.name, err))
        print("        %.1fs, %d KB" % (result["seconds"], out.stat().st_size // 1024))
        written += 1

    print("\n%d written, %d already present." % (written, skipped))
    print("These are unreviewed drafts. Have a Singapore Hokkien speaker listen")
    print("before this goes in front of anyone — that is assumption 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
