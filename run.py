#!/usr/bin/env python3
"""Dialect Money pipeline.

    python3 run.py <whitelisted-url> [--topic "..."] [--tts script|mandarin|hokkien]

Runs: fetch -> summarise (EN) -> translate (ZH) -> translate (Hokkien) ->
integrity check -> narration. Writes every intermediate artefact to out/ so each
stage can be reviewed on its own, which is the point: the Mandarin file is the
one a human can actually check before anything is spoken aloud.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from pipeline import integrity, tts
from pipeline.fetch import fetch_page
from pipeline.llm import LLMError
from pipeline.summarise import summarise
from pipeline.translate import to_hokkien, to_mandarin
from pipeline.whitelist import NotWhitelisted

OUT_DIR = Path(__file__).parent / "out"


def load_env(path=None):
    """Load KEY=VALUE lines from .env into the environment. No dependency."""
    env_path = Path(path or Path(__file__).parent / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def slug(url):
    """Filesystem-safe stem from a URL path."""
    tail = re.sub(r"[^a-z0-9]+", "-", url.lower().split("//")[-1]).strip("-")
    return (tail[-60:] or "explainer").lstrip("-")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="Whitelisted source page (CPF, MAS, MoneySense, IRAS, MOF, gov.sg)")
    parser.add_argument("--topic", help="Optional focus, e.g. 'what a rider covers'")
    parser.add_argument("--tts", default="script", choices=("script", "mandarin", "hokkien"),
                        help="Narration backend (default: script, for a human reader)")
    args = parser.parse_args(argv)

    load_env()
    OUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    stem = OUT_DIR / f"{stamp}-{slug(args.url)}"

    try:
        print(f"[1/5] Fetching {args.url}")
        page = fetch_page(args.url)
        print(f"      {len(page['text']):,} characters of text")

        print("[2/5] Summarising to an English explainer script")
        english = summarise(page, args.topic)
        (stem.with_suffix(".en.txt")).write_text(english, encoding="utf-8")
        print(f"      {len(english.split())} words")

        print("[3/5] Translating to Chinese")
        mandarin = to_mandarin(english)
        (stem.with_suffix(".zh.txt")).write_text(mandarin, encoding="utf-8")

        print("[4/5] Translating to Hokkien")
        hokkien = to_hokkien(mandarin)
        if hokkien.get("parse_failed"):
            print("      warning: model did not return JSON; treating reply as Han text")
        (stem.with_suffix(".nan.json")).write_text(
            json.dumps(hokkien, ensure_ascii=False, indent=2), encoding="utf-8")

        print("[5/5] Checking figures survived translation")
        result = integrity.check(english,
                                 ("Chinese", mandarin),
                                 ("Hokkien", hokkien.get("han", "")))
        print("      " + integrity.format_report(result).replace("\n", "\n      "))

        narration = tts.synthesise(args.tts, hokkien=hokkien, mandarin=mandarin,
                                   source_url=args.url, out_stem=str(stem))
        print(f"      narration: {narration['path']}")
        if narration.get("warning"):
            print(f"      WARNING: {narration['warning']}")

    except NotWhitelisted as err:
        sys.exit(f"Blocked: {err}")
    except (LLMError, tts.TTSError) as err:
        sys.exit(f"Failed: {err}")

    print(f"\nArtefacts written to {OUT_DIR}/")
    if not result["ok"]:
        sys.exit("Integrity check FAILED - do not publish. See figures above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
