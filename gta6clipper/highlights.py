"""Find the most exciting moments in a video from cheap signals.

Signals (all optional except loudness):
  * loudness      - yelling, gunfire, explosions, crashes are loud
  * spikes        - sudden jumps in volume relative to the last few seconds
  * heatmap       - YouTube's "most replayed" graph, when the video has one
  * keyword hits  - hype words in the transcript ("no way", "clip that", ...)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from .transcribe import Word


@dataclass
class Highlight:
    start: float
    end: float
    peak: float
    score: float
    reasons: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end - self.start


def _robust_z(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return x
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826
    spread = mad if mad > 1e-6 else (np.std(x) or 1.0)
    return np.clip((x - med) / spread, -3.0, 6.0)


def _smooth(x: np.ndarray, width: int) -> np.ndarray:
    if width <= 1 or x.size == 0:
        return x
    kernel = np.ones(width) / width
    return np.convolve(x, kernel, mode="same")


def _trailing_mean(x: np.ndarray, width: int) -> np.ndarray:
    csum = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    idx = np.arange(1, x.size + 1)
    lo = np.maximum(0, idx - width)
    return ((csum[idx] - csum[lo]) / (idx - lo)).astype(np.float32)


def heatmap_curve(heatmap: list[dict] | None, n: int, hop: float) -> np.ndarray | None:
    """Resample yt-dlp's heatmap [{start_time, end_time, value}] onto our time grid."""
    if not heatmap:
        return None
    times = np.arange(n) * hop
    out = np.zeros(n, dtype=np.float32)
    for seg in heatmap:
        mask = (times >= float(seg["start_time"])) & (times < float(seg["end_time"]))
        out[mask] = float(seg.get("value", 0.0))
    return out


def keyword_hits(words: list[Word], keywords: list[str]) -> list[tuple[float, str]]:
    """Times where any keyword phrase is spoken."""
    norm = [re.sub(r"[^a-z0-9' ]", "", w.text.lower()).strip() for w in words]
    hits: list[tuple[float, str]] = []
    phrases = [k.lower().split() for k in keywords if k.strip()]
    for i in range(len(norm)):
        for phrase in phrases:
            if norm[i : i + len(phrase)] == phrase:
                hits.append((words[i].start, " ".join(phrase)))
    return hits


def score_timeline(
    loudness_db: np.ndarray,
    hop: float,
    heatmap: np.ndarray | None = None,
    hits: list[tuple[float, str]] | None = None,
) -> np.ndarray:
    n = loudness_db.size
    if n == 0:
        return loudness_db
    loud = _robust_z(_smooth(loudness_db, max(1, int(2 / hop))))
    spike = np.maximum(loudness_db - _trailing_mean(loudness_db, max(1, int(10 / hop))), 0.0)
    spike = _robust_z(_smooth(spike, max(1, int(1 / hop))))
    score = 0.6 * loud + 0.4 * spike
    if heatmap is not None and heatmap.size == n and heatmap.max() > 0:
        score = score + 3.0 * (heatmap / heatmap.max())
    if hits:
        times = np.arange(n) * hop
        for t, _ in hits:
            score = score + 2.0 * np.exp(-((times - t) ** 2) / (2 * 2.0**2))
    return score.astype(np.float32)


def pick_peaks(score: np.ndarray, hop: float, count: int, min_gap: float, skip_edges: float = 3.0) -> list[int]:
    """Greedy non-maximum suppression: best moment, blank out its neighbourhood, repeat."""
    s = score.astype(np.float64).copy()
    edge = int(skip_edges / hop)
    if s.size > 2 * edge + 1:
        s[:edge] = -np.inf
        s[-edge:] = -np.inf
    gap = max(1, int(min_gap / hop))
    peaks: list[int] = []
    while len(peaks) < count:
        i = int(np.argmax(s))
        if not np.isfinite(s[i]):
            break
        peaks.append(i)
        s[max(0, i - gap) : i + gap + 1] = -np.inf
    return peaks


def window_around(peak_t: float, length: float, duration: float, lead: float = 0.6) -> tuple[float, float]:
    """Clip window that puts the peak a bit past the middle (build-up, then payoff)."""
    length = min(length, duration)
    start = max(0.0, peak_t - lead * length)
    end = start + length
    if end > duration:
        end = duration
        start = max(0.0, end - length)
    return start, end


def snap_to_speech(start: float, end: float, words: list[Word], pad: float = 0.15) -> tuple[float, float]:
    """Don't cut someone off mid-word: move cut points to the edges of the word they land in."""
    for w in words:
        if w.start < start < w.end:
            start = max(0.0, w.start - pad)
        if w.start < end < w.end:
            end = w.end + pad
    return start, end


def find_highlights(
    score: np.ndarray,
    hop: float,
    duration: float,
    count: int,
    length: float,
    min_gap: float,
    hits: list[tuple[float, str]] | None = None,
) -> list[Highlight]:
    """Top-N highlights, best first."""
    out: list[Highlight] = []
    for i in pick_peaks(score, hop, count, min_gap):
        t = i * hop
        start, end = window_around(t, length, duration)
        reasons = sorted({phrase for ht, phrase in (hits or []) if start <= ht <= end})
        out.append(Highlight(start=start, end=end, peak=t, score=float(score[i]), reasons=reasons))
    return out
