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

Needs the Hokkien TTS extras and ffmpeg:

    .venv/bin/pip install torch omnivoice soundfile transformers
    brew install ffmpeg          # or apt-get install ffmpeg
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA = ROOT / "site" / "explainers.js"
AUDIO_DIR = ROOT / "site" / "audio"
DIALECT = "hokkien"

# Narration speed. Below 1.0 is slower, which suits an elderly listener.
SPEED = 0.9

# 24 kbps mono is ample for speech and keeps the repo light — a 20-second clip
# lands around 60 KB, so the whole set stays well under a megabyte.
MP3_BITRATE = "24k"


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
    """Yield (explainer_id, line_index, han_text) for every clip to render."""
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


def target(explainer_id, index):
    return AUDIO_DIR / ("%s.%s.%d.mp3" % (explainer_id, DIALECT, index))


def to_mp3(wav_path, mp3_path):
    """Transcode with ffmpeg. Speech at 24 kbps mono keeps the repo small."""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-ac", "1", "-b:a", MP3_BITRATE, str(mp3_path)],
        check=True,
    )


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

    if not shutil.which("ffmpeg"):
        raise SystemExit(
            "ffmpeg is not on PATH, and the site asks for .mp3.\n"
            "  brew install ffmpeg      (macOS)\n"
            "  apt-get install ffmpeg   (Debian/Ubuntu)"
        )

    from pipeline import tts  # imported here so --dry-run needs no torch

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    written = skipped = 0

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "clip.wav"
        for explainer_id, index, line in work:
            out = target(explainer_id, index)
            if out.exists() and not args.force:
                skipped += 1
                continue
            print("  %s" % out.name, flush=True)
            try:
                tts.say_hokkien(line, str(scratch), speed=SPEED)
                to_mp3(scratch, out)
            except tts.TTSError as err:
                raise SystemExit("Narration failed on %s: %s" % (out.name, err))
            except subprocess.CalledProcessError as err:
                raise SystemExit("ffmpeg failed on %s: %s" % (out.name, err))
            written += 1

    print("\n%d written, %d already present." % (written, skipped))
    print("These are unreviewed drafts. Have a Singapore Hokkien speaker listen")
    print("before this goes in front of anyone — that is assumption 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
