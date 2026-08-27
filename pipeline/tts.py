"""Stage 4: narration.

Backends are pluggable because the Hokkien voice is the least settled part of
this product, and the problem statement ranks it as assumption 2 - untested, and
fatal to trust if the voice is poor.

Available today:

  script    Writes a narration script for a human Hokkien speaker to read.
            The problem statement names human recording as a credible v1 route,
            and it sidesteps the trust risk of synthetic financial narration.

  mandarin  macOS `say` with a Mandarin voice. This is NOT Hokkien. It exists
            only to prove the pipeline plumbing end to end, and every file it
            writes is named and labelled to make that impossible to forget.

  hokkien   MERaLiON-OmniVoice-Hokkien-TTS, A*STAR's Singapore Hokkien model.
            Runs locally - no API key, no per-character cost, nothing leaving
            the machine. Takes Hokkien written in Han characters and produces
            Singapore Hokkien speech.

On the choice of MERaLiON over a commercial vendor: it is fine-tuned on Hokkien
conversational data for *Singapore*, so it avoids the Quanzhou/Zhangzhou accent
mismatch and the Japanese loanwords that come with Taiwanese-trained voices. For
a project whose guardrail is "authoritative Singapore sources only", narrating
with an A*STAR model rather than a foreign vendor is also the more defensible
provenance.

Note its licence is the MERaLiON-3 Public Licence, not a standard OSS licence.
Check it before publishing anything beyond coursework.
"""

import os
import subprocess

# macOS Mandarin voices, best first. Grandma/Grandpa read noticeably slower,
# which suits the audience even though the language is wrong.
MANDARIN_VOICES = ("Grandma (Chinese (China mainland))", "Tingting", "Meijia")

NOT_HOKKIEN_WARNING = (
    "This audio is MANDARIN, not Hokkien. It exists to test the pipeline, "
    "not to be played to a senior as a dialect explainer."
)


class TTSError(Exception):
    """Raised when narration cannot be produced."""


def available_mandarin_voice():
    """First installed voice from MANDARIN_VOICES, or None."""
    try:
        listing = subprocess.run(
            ["say", "-v", "?"], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None

    for voice in MANDARIN_VOICES:
        if voice.split(" (")[0] in listing:
            return voice
        if voice in listing:
            return voice
    return None


def say_mandarin(text, out_path, rate=150):
    """Narrate Mandarin text to an .aiff via macOS `say`. NOT Hokkien.

    rate defaults slow (150 wpm vs the ~175 default) for an elderly listener.
    """
    voice = available_mandarin_voice()
    if not voice:
        raise TTSError("No macOS Mandarin voice found; cannot produce sample audio.")

    try:
        subprocess.run(
            ["say", "-v", voice, "-r", str(rate), "-o", out_path, text],
            check=True, capture_output=True, timeout=300,
        )
    except subprocess.CalledProcessError as err:
        raise TTSError(f"say failed: {err.stderr.decode('utf-8', 'replace')[:300]}") from err
    except OSError as err:
        raise TTSError(f"say is unavailable on this system: {err}") from err

    return {"path": out_path, "voice": voice, "language": "Mandarin",
            "warning": NOT_HOKKIEN_WARNING}


def write_recording_script(hokkien, source_url, out_path):
    """Write a script for a human Hokkien speaker to record."""
    lines = [
        "HOKKIEN NARRATION SCRIPT",
        f"Source: {source_url}",
        "",
        "Read this aloud in colloquial Singapore Hokkien, unhurried, as if",
        "explaining to a parent. Every figure below is from the cited source -",
        "if any of it sounds wrong to you, stop and flag it rather than adapting.",
        "",
        "=" * 64,
        "HAN CHARACTERS",
        "=" * 64,
        hokkien.get("han", ""),
    ]

    if hokkien.get("tailo"):
        lines += ["", "=" * 64, "TAI-LO ROMANISATION", "=" * 64,
                  hokkien["tailo"]]

    if hokkien.get("register_notes"):
        lines += ["", "=" * 64, "REGISTER NOTES FOR THE READER", "=" * 64,
                  hokkien["register_notes"]]

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    return {"path": out_path, "language": "Hokkien", "mode": "human recording"}


MERALION_MODEL = "MERaLiON/MERaLiON-OmniVoice-Hokkien-TTS"

# Loading the model takes tens of seconds, so keep one per process.
_meralion_cache = {}


def _load_meralion():
    """Load MERaLiON once, preferring Apple Silicon MPS, then CUDA, then CPU.

    Imported lazily so the rest of the pipeline runs without torch installed -
    the `script` backend needs nothing but the standard library.
    """
    if "model" in _meralion_cache:
        return _meralion_cache["model"]

    try:
        import torch
        from omnivoice.models.omnivoice import OmniVoice
    except ImportError as err:
        raise TTSError(
            "Hokkien TTS needs torch and omnivoice. Install them into the project "
            "venv:  .venv/bin/pip install torch omnivoice soundfile transformers"
        ) from err

    # Apple Silicon MPS is deliberately NOT used. Measured on an M4 (torch
    # 2.13, omnivoice 0.2.1): this model hard-crashes with SIGBUS during load
    # on MPS at both float16 and float32 - a native crash, not a Python
    # exception, so it cannot be caught and fallen back from in-process.
    # CPU float32 loads in ~2s and generates a short clip in ~7s, which is
    # ample for a batch-publishing pipeline.
    if torch.cuda.is_available():
        device, dtype = "cuda:0", torch.float16
    else:
        device, dtype = "cpu", torch.float32

    try:
        model = OmniVoice.from_pretrained(MERALION_MODEL, device_map=device, dtype=dtype)
    except Exception as err:  # model download or device placement
        raise TTSError(f"Could not load {MERALION_MODEL} on {device}: {err}") from err

    _meralion_cache["model"] = model
    _meralion_cache["device"] = device
    return model


def say_hokkien(han_text, out_path, speed=None):
    """Narrate Hokkien written in Han characters via MERaLiON. Returns a dict.

    The input must be HOKKIEN in Han characters, not Mandarin. Feeding Mandarin
    text here does not error - it yields a literary reading (讀書音): real
    Hokkien phonology wrapped around Mandarin vocabulary, which sounds stilted
    and broadcast-like rather than like a person talking. translate.to_hokkien
    is what produces the correct input.
    """
    if not han_text.strip():
        raise TTSError("No Hokkien text to narrate.")

    import soundfile

    model = _load_meralion()

    kwargs = {"text": han_text, "language": "nan"}  # nan = Min Nan
    if speed is not None:
        kwargs["speed"] = speed

    try:
        audios = model.generate(**kwargs)
    except Exception as err:
        raise TTSError(f"MERaLiON generation failed: {err}") from err

    rate = getattr(model, "sampling_rate", 24000)
    soundfile.write(out_path, audios[0], rate)

    return {
        "path": out_path,
        "language": "Hokkien (Singapore)",
        "model": MERALION_MODEL,
        "device": _meralion_cache.get("device"),
        "seconds": round(len(audios[0]) / rate, 1),
    }


def synthesise(backend, *, hokkien, mandarin, source_url, out_stem, speed=None):
    """Dispatch to a backend. Returns a dict describing what was produced."""
    if backend == "script":
        return write_recording_script(hokkien, source_url, f"{out_stem}.script.txt")

    if backend == "mandarin":
        return say_mandarin(mandarin, f"{out_stem}.MANDARIN-NOT-HOKKIEN.aiff")

    if backend == "hokkien":
        return say_hokkien(hokkien.get("han", ""), f"{out_stem}.hokkien.wav", speed)

    raise TTSError(f"Unknown TTS backend: {backend!r}. Use script, mandarin or hokkien.")
