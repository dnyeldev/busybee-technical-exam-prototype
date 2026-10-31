"""Turn a time window of the source video into a finished clip file."""

from __future__ import annotations

import tempfile
from pathlib import Path

from .media import run_ffmpeg, video_encoder_args

SHORT_W, SHORT_H = 1080, 1920
LONG_W, LONG_H = 1920, 1080


def _vertical_filter(layout: str) -> str:
    if layout == "crop":
        return f"scale=-2:{SHORT_H},crop={SHORT_W}:{SHORT_H}"
    # Full gameplay frame in the middle, blurred zoomed copy filling the rest.
    return (
        f"split=2[bg][fg];"
        f"[bg]scale={SHORT_W}:{SHORT_H}:force_original_aspect_ratio=increase,crop={SHORT_W}:{SHORT_H},"
        f"boxblur=20:2,eq=brightness=-0.08[bgb];"
        f"[fg]scale={SHORT_W}:-2[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
    )


def _horizontal_filter() -> str:
    return (
        f"scale={LONG_W}:{LONG_H}:force_original_aspect_ratio=decrease,"
        f"pad={LONG_W}:{LONG_H}:(ow-iw)/2:(oh-ih)/2"
    )


def render_clip(
    source: str | Path,
    out_path: str | Path,
    start: float,
    end: float,
    vertical: bool,
    cfg: dict,
    ass_text: str | None = None,
    fade: float = 0.0,
    has_audio: bool = True,
) -> Path:
    source, out_path = Path(source).resolve(), Path(out_path).resolve()
    duration = end - start
    vf = _vertical_filter(cfg["shorts"]["layout"]) if vertical else _horizontal_filter()
    vf += ",setsar=1,format=yuv420p"
    if fade > 0:
        vf += f",fade=t=in:st=0:d={fade:.2f},fade=t=out:st={max(0.0, duration - fade):.2f}:d={fade:.2f}"

    af = [f"afade=t=in:st=0:d=0.15", f"afade=t=out:st={max(0.0, duration - 0.3):.2f}:d=0.3"]
    if fade > 0:
        af = [f"afade=t=in:st=0:d={fade:.2f}", f"afade=t=out:st={max(0.0, duration - fade):.2f}:d={fade:.2f}"]
    if cfg["render"].get("loudnorm", True):
        af.append("loudnorm=I=-14:TP=-1.5:LRA=11")
    af.append("aresample=48000")

    with tempfile.TemporaryDirectory() as tmp:
        if ass_text:
            # ffmpeg filter paths are fussy about special characters; run inside the temp dir instead.
            (Path(tmp) / "captions.ass").write_text(ass_text, encoding="utf-8")
            vf += ",ass=captions.ass"
        args = ["-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(source)]
        if not has_audio:
            args += ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        args += [
            "-filter_complex", f"[0:v]{vf}[v];[{0 if has_audio else 1}:a]{','.join(af)}[a]",
            "-map", "[v]", "-map", "[a]",
            *video_encoder_args(cfg["render"]["encoder"], cfg["render"]["bitrate"]),
            "-c:a", "aac", "-b:a", "192k", "-ac", "2",
            "-movflags", "+faststart",
            str(out_path),
        ]
        run_ffmpeg(args, cwd=tmp)
    return out_path


def concat(parts: list[Path], out_path: str | Path) -> Path:
    """Join already-encoded clips with identical settings (no re-encode)."""
    out_path = Path(out_path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "list.txt"
        listing.write_text("".join(f"file '{str(p.resolve()).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for p in parts))
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
                    "-movflags", "+faststart", str(out_path)])
    return out_path
