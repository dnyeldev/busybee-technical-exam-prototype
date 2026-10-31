"""Settings: built-in defaults, optionally overridden by a config.toml."""

from __future__ import annotations

import copy
import tomllib
from pathlib import Path

DEFAULTS: dict = {
    "output_dir": "clips",
    "download_dir": "downloads",
    "shorts": {
        "enabled": True,
        "count": 8,             # how many vertical clips per video
        "target_seconds": 30,   # typical clip length
        "min_seconds": 12,
        "layout": "blur",       # "blur" = full gameplay frame on blurred background, "crop" = zoomed center crop
        "title_banner": True,   # big title text at the top of the vertical frame
    },
    "longform": {
        "enabled": True,
        "count": 10,            # highlights stitched into one 16:9 compilation
        "clip_seconds": 40,
        "fade_seconds": 0.4,
        "captions": False,
    },
    "captions": {
        "enabled": True,
        "backend": "auto",      # "auto", "mlx" (Apple Silicon), "faster-whisper" (CPU)
        "model": "small",       # tiny / base / small / medium / large-v3 / large-v3-turbo
        "language": "en",
        "font": "Arial Black",
        "font_size": 88,
        "words_per_chunk": 3,
    },
    "detect": {
        # deep = transcribe the WHOLE video and also score hype words (slower, better picks).
        # Off: only loudness / "most replayed" decide, and only the chosen clips get transcribed.
        "deep": False,
        "min_gap_seconds": 45,  # don't pick two highlights closer than this
        "keywords": [
            "oh my god", "no way", "let's go", "lets go", "what the", "bro", "holy",
            "insane", "crazy", "clip that", "clip it", "run", "cops", "wanted",
            "five stars", "5 stars", "explosion", "crash", "heist", "jason", "lucia",
            "vice city", "wasted", "busted", "yo", "dude", "wow", "nah",
        ],
    },
    "sources": {
        # Channels you have permission to clip (name, @handle, channel id, or channel URL).
        # Anything else needs --permission "<note>" so there's a record of who said yes.
        "allowed_channels": [],
        "max_height": 1080,
        "cookies_from_browser": "",  # e.g. "chrome" or "safari" if YouTube asks you to sign in
    },
    "render": {
        "encoder": "auto",      # "auto" uses the Mac's hardware encoder when available
        "bitrate": "12M",
        "loudnorm": True,       # even out volume to streaming-platform loudness
    },
    "metadata": {
        "title_prefix": "GTA 6",
        "hashtags": ["#GTA6", "#GTAVI", "#GTA", "#ViceCity", "#Gaming"],
        "shorts_hashtags": ["#Shorts"],
    },
}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(path: str | Path | None = None) -> dict:
    """Load defaults, then layer config.toml (explicit path, or ./config.toml if present)."""
    candidate = Path(path) if path else Path("config.toml")
    if path and not candidate.exists():
        raise FileNotFoundError(f"Config file not found: {candidate}")
    if candidate.exists():
        with candidate.open("rb") as fh:
            return _merge(DEFAULTS, tomllib.load(fh))
    return copy.deepcopy(DEFAULTS)
