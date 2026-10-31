"""Thin wrappers around ffmpeg / ffprobe."""

from __future__ import annotations

import functools
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np


class FFmpegMissing(RuntimeError):
    pass


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise FFmpegMissing(f"{tool} not found. On a Mac run:  brew install ffmpeg")


def probe(path: str | Path) -> dict:
    """Return duration, width, height, fps, has_audio for a media file."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"No video stream in {path}")
    num, _, den = (video.get("avg_frame_rate") or "30/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    return {
        "duration": float(data["format"].get("duration") or video.get("duration") or 0.0),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": fps or 30.0,
        "has_audio": any(s.get("codec_type") == "audio" for s in data["streams"]),
    }


def loudness_curve(path: str | Path, hop: float = 0.5, sample_rate: int = 8000) -> np.ndarray:
    """Loudness in dBFS for every `hop` seconds of audio, streamed so long VODs don't fill RAM."""
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sample_rate),
         "-f", "s16le", "-"],
        stdout=subprocess.PIPE,
    )
    block = int(hop * sample_rate) * 2  # 16-bit samples
    values: list[float] = []
    assert proc.stdout is not None
    while True:
        chunk = proc.stdout.read(block)
        if len(chunk) < 2:
            break
        samples = np.frombuffer(chunk[: len(chunk) // 2 * 2], dtype=np.int16).astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(samples * samples))) if samples.size else 0.0
        values.append(20.0 * np.log10(max(rms, 1e-5)))
    proc.wait()
    return np.asarray(values, dtype=np.float32)


@functools.cache
def _encoders() -> str:
    return subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout


def video_encoder_args(choice: str, bitrate: str) -> list[str]:
    """Hardware H.264 on macOS (VideoToolbox) when available, otherwise libx264."""
    use_hw = choice == "videotoolbox" or (
        choice == "auto" and sys.platform == "darwin" and "h264_videotoolbox" in _encoders()
    )
    if use_hw:
        return ["-c:v", "h264_videotoolbox", "-b:v", bitrate, "-maxrate", bitrate, "-bufsize", bitrate,
                "-profile:v", "high", "-allow_sw", "1"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-maxrate", bitrate, "-bufsize", bitrate]


def run_ffmpeg(args: list[str], cwd: str | Path | None = None) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(cmd)}\n{result.stderr.strip()}")
