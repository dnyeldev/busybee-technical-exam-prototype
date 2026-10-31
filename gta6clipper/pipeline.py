"""Glue: source video in -> folder of finished clips + post text out."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from . import captions as cap
from . import highlights as hl
from . import metadata as meta
from .media import loudness_curve, probe, require_ffmpeg
from .render import LONG_H, LONG_W, SHORT_H, SHORT_W, concat, render_clip
from .sources import Source, resolve
from .transcribe import Transcriber, TranscriptionUnavailable, Word

HOP = 0.5


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")[:60] or "video"


class Pipeline:
    def __init__(self, cfg: dict, log=print):
        self.cfg = cfg
        self.log = log
        self._transcriber: Transcriber | None = None
        self._transcriber_failed = False

    def transcriber(self) -> Transcriber | None:
        if not self.cfg["captions"]["enabled"] or self._transcriber_failed:
            return None
        if self._transcriber is None:
            c = self.cfg["captions"]
            try:
                self._transcriber = Transcriber(c["model"], c.get("language"), c.get("backend", "auto"))
            except TranscriptionUnavailable as exc:
                self.log(f"  ! {exc} Continuing without captions.")
                self._transcriber_failed = True
                return None
        return self._transcriber

    def words_for(self, path: Path, start: float, end: float, full: list[Word] | None) -> list[Word]:
        if full is not None:
            return [w for w in full if w.end > start and w.start < end]
        t = self.transcriber()
        return t.words(path, start, end) if t else []

    def run(self, value: str, permission_note: str | None = None) -> Path:
        require_ffmpeg()
        t0 = time.time()
        source = resolve(value, self.cfg, permission_note)
        info = probe(source.path)
        duration = info["duration"]
        out_dir = Path(self.cfg["output_dir"]).expanduser().resolve() / (
            f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(source.title)}"
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"Clipping: {source.title}  ({duration / 60:.1f} min)  ->  {out_dir}")

        self.log("  Listening for loud / hype moments...")
        loud = loudness_curve(source.path, HOP) if info["has_audio"] else np.zeros(int(duration / HOP) + 1, dtype=np.float32)

        full_words: list[Word] | None = None
        hits: list[tuple[float, str]] = []
        if self.cfg["detect"]["deep"] and self.transcriber():
            self.log("  Deep mode: transcribing the whole video (this is the slow part)...")
            full_words = self.transcriber().words(source.path)
            hits = hl.keyword_hits(full_words, self.cfg["detect"]["keywords"])
            self.log(f"  Found {len(hits)} hype-word moments.")

        heat = hl.heatmap_curve(source.heatmap, loud.size, HOP)
        if heat is not None:
            self.log("  Using YouTube 'most replayed' data.")
        score = hl.score_timeline(loud, HOP, heat, hits)

        summary: dict = {"source": source.as_record(), "shorts": [], "longform": None}
        if self.cfg["shorts"]["enabled"]:
            summary["shorts"] = self._shorts(source, info, score, hits, full_words, out_dir)
        if self.cfg["longform"]["enabled"]:
            summary["longform"] = self._longform(source, info, score, hits, full_words, out_dir)

        (out_dir / "source.json").write_text(json.dumps(source.as_record(), indent=2))
        (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        self.log(f"Done in {time.time() - t0:.0f}s -> {out_dir}")
        return out_dir

    def _shorts(self, source: Source, info: dict, score, hits, full_words, out_dir: Path) -> list[dict]:
        c = self.cfg["shorts"]
        found = hl.find_highlights(score, HOP, info["duration"], int(c["count"]), float(c["target_seconds"]),
                                   float(self.cfg["detect"]["min_gap_seconds"]), hits)
        found = [h for h in found if h.duration >= float(c["min_seconds"])]
        results = []
        for n, h in enumerate(found, 1):
            self.log(f"  Short {n}/{len(found)}: {h.start:.0f}s-{h.end:.0f}s (score {h.score:.1f})")
            words = self.words_for(source.path, h.start - 3, h.end + 3, full_words)
            start, end = hl.snap_to_speech(h.start, h.end, words)
            end = min(end, info["duration"])
            in_clip = [w for w in words if w.end > start and w.start < end]
            title = meta.clip_title(self.cfg, meta.hook_text(in_clip, h.reasons), n)
            ass = None
            if in_clip or c.get("title_banner"):
                ass = cap.build_ass(
                    in_clip, start, end, SHORT_W, SHORT_H,
                    font=self.cfg["captions"]["font"], font_size=int(self.cfg["captions"]["font_size"]),
                    per_chunk=int(self.cfg["captions"]["words_per_chunk"]),
                    title=title if c.get("title_banner") else None,
                )
            name = f"short_{n:02d}"
            render_clip(source.path, out_dir / f"{name}.mp4", start, end, True, self.cfg, ass,
                        has_audio=info["has_audio"])
            (out_dir / f"{name}.txt").write_text(meta.short_post(self.cfg, title, source))
            results.append({"file": f"{name}.mp4", "start": round(start, 2), "end": round(end, 2),
                            "score": round(h.score, 2), "title": title, "hype_words": h.reasons})
        return results

    def _longform(self, source: Source, info: dict, score, hits, full_words, out_dir: Path) -> dict | None:
        c = self.cfg["longform"]
        found = hl.find_highlights(score, HOP, info["duration"], int(c["count"]), float(c["clip_seconds"]),
                                   max(float(self.cfg["detect"]["min_gap_seconds"]), float(c["clip_seconds"])),
                                   hits)
        if len(found) < 2:
            self.log("  Video too short for a compilation; skipping long-form.")
            return None
        found.sort(key=lambda h: h.start)  # chronological reads better as a story
        parts_dir = out_dir / "longform_parts"
        parts_dir.mkdir(exist_ok=True)
        parts, chapters, cursor = [], [], 0.0
        for n, h in enumerate(found, 1):
            self.log(f"  Compilation part {n}/{len(found)}")
            ass = None
            if c.get("captions"):
                words = self.words_for(source.path, h.start, h.end, full_words)
                ass = cap.build_ass(words, h.start, h.end, LONG_W, LONG_H, font=self.cfg["captions"]["font"],
                                    font_size=int(self.cfg["captions"]["font_size"]),
                                    per_chunk=int(self.cfg["captions"]["words_per_chunk"]))
            part = render_clip(source.path, parts_dir / f"part_{n:02d}.mp4", h.start, h.end, False, self.cfg,
                               ass, fade=float(c["fade_seconds"]), has_audio=info["has_audio"])
            parts.append(part)
            label = h.reasons[0].title() if h.reasons else f"Moment {n}"
            chapters.append((cursor, label))
            cursor += probe(part)["duration"]
        final = concat(parts, out_dir / "compilation.mp4")
        for p in parts:
            p.unlink()
        parts_dir.rmdir()
        (out_dir / "compilation.txt").write_text(meta.longform_post(self.cfg, source, chapters))
        return {"file": final.name, "duration": round(cursor, 1), "chapters": chapters}
