"""Burned-in, TikTok-style captions as an ASS subtitle file (rendered by ffmpeg/libass)."""

from __future__ import annotations

from .transcribe import Word


def _ts(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _clean(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def chunk_words(words: list[Word], per_chunk: int = 3, max_gap: float = 0.6) -> list[tuple[float, float, str]]:
    """Group words into short punchy lines: (start, end, TEXT)."""
    chunks: list[list[Word]] = []
    for w in words:
        if chunks and len(chunks[-1]) < per_chunk and w.start - chunks[-1][-1].end <= max_gap:
            chunks[-1].append(w)
        else:
            chunks.append([w])
    lines = []
    for i, group in enumerate(chunks):
        start, end = group[0].start, group[-1].end
        if i + 1 < len(chunks) and chunks[i + 1][0].start - end < 0.35:
            end = chunks[i + 1][0].start  # no flicker between consecutive lines
        text = _clean(" ".join(w.text for w in group)).upper()
        if text:
            lines.append((start, max(end, start + 0.2), text))
    return lines


def build_ass(
    words: list[Word],
    clip_start: float,
    clip_end: float,
    width: int,
    height: int,
    font: str = "Arial Black",
    font_size: int = 88,
    per_chunk: int = 3,
    title: str | None = None,
) -> str:
    """ASS document; word times are absolute and get shifted to clip-relative."""
    scale = height / 1920 if height > width else height / 1080
    size = max(24, int(font_size * (scale if height > width else scale * 0.75)))
    margin_v = int(height * 0.22) if height > width else int(height * 0.08)
    outline = max(2, int(size / 12))
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},2,2,60,60,{margin_v},1
Style: Title,{font},{int(size * 0.8)},&H0000E5FF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},2,8,60,60,{int(height * 0.12)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    duration = clip_end - clip_start
    if title:
        events.append(f"Dialogue: 1,{_ts(0)},{_ts(duration)},Title,,0,0,0,,{_clean(title).upper()}")
    inside = [w for w in words if w.end > clip_start and w.start < clip_end]
    for start, end, text in chunk_words(inside, per_chunk):
        s, e = start - clip_start, min(end, clip_end) - clip_start
        pop = r"{\fscx112\fscy112\t(0,120,\fscx100\fscy100)}"
        events.append(f"Dialogue: 0,{_ts(s)},{_ts(e)},Caption,,0,0,0,,{pop}{text}")
    return header + "\n".join(events) + "\n"
