#!/usr/bin/env python3
"""MERaLiON Hokkien TTS as an MCP server.

Why an MCP server rather than a CLI: the model costs a couple of seconds to
load and the process then holds it in memory. A CLI pays that on every
invocation; a long-lived server pays it once and every subsequent clip is just
generation time. It also makes the voice callable from any MCP client, not only
this pipeline.

Register it with Claude Code (from the project directory):

    claude mcp add hokkien-tts -- ./.venv/bin/python mcp_server.py

Tools exposed:
    speak_hokkien       Hokkien in Han characters -> a .wav file
    hokkien_status      What is loaded, on what device, and how fast

IMPORTANT: speak_hokkien expects HOKKIEN written in Han characters, not
Mandarin. Mandarin text does not error - it produces a literary reading
(讀書音), which sounds stilted and broadcast-like rather than like a person
speaking. Use the pipeline's translate step to produce correct input.
"""

import sys
import time
from pathlib import Path

from mcp.server.mcpserver import MCPServer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import tts  # noqa: E402

DEFAULT_OUT_DIR = Path(__file__).resolve().parent / "out"

server = MCPServer(
    name="hokkien-tts",
    title="MERaLiON Singapore Hokkien TTS",
    version="0.1.0",
    instructions=(
        "Generates spoken Singapore Hokkien audio from Hokkien text written in "
        "Han characters, using A*STAR's MERaLiON-OmniVoice-Hokkien-TTS locally. "
        "Input must be Hokkien, not Mandarin: Mandarin text yields a stilted "
        "literary reading rather than natural speech. Runs on CPU; the first "
        "call loads the model and later calls reuse it."
    ),
)

_stats = {"calls": 0, "last_load_s": None, "last_generate_s": None}


@server.tool(
    name="speak_hokkien",
    title="Speak Hokkien text",
    description=(
        "Narrate Hokkien text (written in Han characters) as Singapore Hokkien "
        "speech, saved as a .wav file. Input MUST be colloquial Hokkien in Han "
        "characters - for example 你阿母煮的菜真好食 - not Mandarin. Passing "
        "Mandarin produces a stilted literary reading instead of natural speech. "
        "Returns the output path and duration."
    ),
)
def speak_hokkien(han_text: str, out_path: str = "", speed: float = 0.0) -> dict:
    """Generate Hokkien speech.

    han_text: Hokkien in Han characters.
    out_path: where to write the .wav. Defaults to a timestamped file in out/.
    speed:    playback speed; 0 means the model default. Below 1.0 is slower,
              which suits an elderly listener.
    """
    if not han_text.strip():
        return {"ok": False, "error": "han_text is empty."}

    if out_path:
        target = Path(out_path)
    else:
        DEFAULT_OUT_DIR.mkdir(exist_ok=True)
        target = DEFAULT_OUT_DIR / f"hokkien-{time.strftime('%Y%m%d-%H%M%S')}.wav"
    target.parent.mkdir(parents=True, exist_ok=True)

    started = time.time()
    already_loaded = "model" in tts._meralion_cache
    try:
        result = tts.say_hokkien(
            han_text, str(target), speed=(speed or None)
        )
    except tts.TTSError as err:
        return {"ok": False, "error": str(err)}

    elapsed = time.time() - started
    _stats["calls"] += 1
    _stats["last_generate_s"] = round(elapsed, 1)
    if not already_loaded:
        _stats["last_load_s"] = round(elapsed, 1)

    return {
        "ok": True,
        "path": result["path"],
        "seconds_of_audio": result["seconds"],
        "took_s": round(elapsed, 1),
        "device": result["device"],
        "model": result["model"],
        "model_was_warm": already_loaded,
        "characters": len(han_text),
    }


@server.tool(
    name="hokkien_status",
    title="Hokkien TTS status",
    description=(
        "Report whether the Hokkien model is loaded, which device it is on, and "
        "timings from recent calls. Useful for checking whether the next call "
        "will pay the model load cost."
    ),
)
def hokkien_status() -> dict:
    """Report model and timing state without triggering a load."""
    loaded = "model" in tts._meralion_cache
    return {
        "model": tts.MERALION_MODEL,
        "loaded": loaded,
        "device": tts._meralion_cache.get("device") if loaded else None,
        "calls_this_session": _stats["calls"],
        "last_load_s": _stats["last_load_s"],
        "last_generate_s": _stats["last_generate_s"],
        "note": (
            "Input must be Hokkien in Han characters, not Mandarin. "
            "Measured on an M4 CPU: first call ~11s (model load included), "
            "later calls ~5s for a short phrase."
        ),
    }


if __name__ == "__main__":
    server.run(transport="stdio")
