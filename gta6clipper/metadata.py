"""Ready-to-paste titles, descriptions and hashtags (template based, no paid AI)."""

from __future__ import annotations

from .sources import Source
from .transcribe import Word


def _fmt(t: float) -> str:
    t = int(t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def hook_text(words: list[Word], reasons: list[str], max_words: int = 6) -> str:
    """A short hook for the title: the hype phrase if one was said, otherwise the first words."""
    if reasons:
        return reasons[0].upper() + "!"
    text = " ".join(w.text for w in words[:max_words]).strip(" ,.")
    return text if len(text) >= 8 else ""


def clip_title(cfg: dict, hook: str, index: int) -> str:
    prefix = cfg["metadata"]["title_prefix"]
    return f"{prefix}: {hook}" if hook else f"{prefix} moment #{index}"


def credit_line(source: Source) -> str:
    if source.own or not source.channel:
        return ""
    return f"Clipped from {source.channel}" + (f" - {source.url}" if source.url else "")


def short_post(cfg: dict, title: str, source: Source) -> str:
    tags = " ".join(cfg["metadata"]["hashtags"] + cfg["metadata"]["shorts_hashtags"])
    lines = [f"TITLE: {title[:95]}", "", "CAPTION:", title, ""]
    if credit_line(source):
        lines += [credit_line(source), ""]
    lines.append(tags)
    return "\n".join(lines) + "\n"


def longform_post(cfg: dict, source: Source, chapters: list[tuple[float, str]]) -> str:
    prefix = cfg["metadata"]["title_prefix"]
    lines = [f"TITLE: {prefix} - Best Moments ({source.title})"[:107], "", "DESCRIPTION:"]
    lines.append(f"The best moments from {source.title}.")
    if credit_line(source):
        lines.append(credit_line(source))
    lines += ["", "Chapters:"]
    lines += [f"{_fmt(t)} {label}" for t, label in chapters]
    lines += ["", " ".join(cfg["metadata"]["hashtags"])]
    return "\n".join(lines) + "\n"
