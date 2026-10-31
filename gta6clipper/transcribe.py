"""Local speech-to-text with word timestamps (free, runs on your Mac).

Backends:
  mlx             - mlx-whisper, uses the Apple Silicon GPU (fastest on M1/M2/M3/M4)
  faster-whisper  - CPU, works everywhere (Intel Macs, Linux)
"""

from __future__ import annotations

import importlib.util
import platform
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .media import run_ffmpeg


@dataclass
class Word:
    start: float
    end: float
    text: str


class TranscriptionUnavailable(RuntimeError):
    pass


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def pick_backend(choice: str) -> str:
    if choice != "auto":
        return choice
    apple_silicon = sys.platform == "darwin" and platform.machine() == "arm64"
    if apple_silicon and _has("mlx_whisper"):
        return "mlx"
    if _has("faster_whisper"):
        return "faster-whisper"
    if _has("mlx_whisper"):
        return "mlx"
    raise TranscriptionUnavailable(
        "No speech-to-text engine installed. Run ./setup.sh again, or use --no-captions."
    )


def _mlx_repo(model: str) -> str:
    if "/" in model:
        return model
    if model == "large-v3-turbo":
        return "mlx-community/whisper-large-v3-turbo"
    return f"mlx-community/whisper-{model}-mlx"


class Transcriber:
    def __init__(self, model: str = "small", language: str | None = "en", backend: str = "auto"):
        self.model_name = model
        self.language = language or None
        self.backend = pick_backend(backend)
        self._fw_model = None

    def _run(self, wav: str) -> list[Word]:
        if self.backend == "mlx":
            import mlx_whisper

            result = mlx_whisper.transcribe(
                wav, path_or_hf_repo=_mlx_repo(self.model_name), word_timestamps=True, language=self.language,
            )
            return [
                Word(float(w["start"]), float(w["end"]), w["word"].strip())
                for seg in result.get("segments", []) for w in seg.get("words", [])
            ]
        if self.backend == "faster-whisper":
            if self._fw_model is None:
                from faster_whisper import WhisperModel

                self._fw_model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
            segments, _ = self._fw_model.transcribe(
                wav, language=self.language, word_timestamps=True, vad_filter=True,
            )
            return [Word(float(w.start), float(w.end), w.word.strip()) for seg in segments for w in (seg.words or [])]
        raise TranscriptionUnavailable(f"Unknown transcription backend: {self.backend}")

    def words(self, media: str | Path, start: float = 0.0, end: float | None = None) -> list[Word]:
        """Words spoken between start and end, with timestamps relative to the whole video."""
        with tempfile.TemporaryDirectory() as tmp:
            wav = str(Path(tmp) / "audio.wav")
            args = ["-ss", f"{start:.3f}"]
            if end is not None:
                args += ["-t", f"{max(0.1, end - start):.3f}"]
            run_ffmpeg([*args, "-i", str(media), "-vn", "-ac", "1", "-ar", "16000", wav])
            words = self._run(wav)
        return [Word(w.start + start, w.end + start, w.text) for w in words if w.text]
