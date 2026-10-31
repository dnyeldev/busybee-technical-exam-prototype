"""Where the footage comes from: a file on your Mac, or a URL you're allowed to clip."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class PermissionNotRecorded(RuntimeError):
    pass


@dataclass
class Source:
    path: Path
    title: str
    own: bool
    url: str | None = None
    channel: str | None = None
    channel_url: str | None = None
    permission_note: str | None = None
    heatmap: list[dict] | None = field(default=None, repr=False)

    def as_record(self) -> dict:
        return {
            "title": self.title, "own_footage": self.own, "url": self.url, "channel": self.channel,
            "channel_url": self.channel_url, "permission_note": self.permission_note, "file": str(self.path),
        }


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value.strip(), re.I))


def channel_allowed(info: dict, allowed: list[str]) -> bool:
    """True if the video's channel matches any entry (name, @handle, channel id, or URL)."""
    ids = {
        str(info.get(k) or "").strip().lower().rstrip("/")
        for k in ("channel", "uploader", "channel_id", "uploader_id", "channel_url", "uploader_url")
    } - {""}
    handles = {i.rsplit("/", 1)[-1] for i in ids if "/" in i}
    for entry in allowed:
        e = entry.strip().lower().rstrip("/")
        if e and (e in ids or e in handles or e.rsplit("/", 1)[-1] in handles | ids):
            return True
    return False


def resolve(value: str, cfg: dict, permission_note: str | None = None) -> Source:
    if not is_url(value):
        path = Path(value).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return Source(path=path.resolve(), title=path.stem, own=True)
    return _download(value, cfg, permission_note)


def _download(url: str, cfg: dict, permission_note: str | None) -> Source:
    try:
        import yt_dlp
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("yt-dlp isn't installed. Run ./setup.sh") from exc

    src_cfg = cfg["sources"]
    opts: dict = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if src_cfg.get("cookies_from_browser"):
        opts["cookiesfrombrowser"] = (src_cfg["cookies_from_browser"],)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    channel = info.get("channel") or info.get("uploader") or "unknown channel"
    allowed = channel_allowed(info, src_cfg.get("allowed_channels", []))
    if not allowed and not permission_note:
        raise PermissionNotRecorded(
            f'"{info.get("title")}" is from {channel}, which isn\'t in allowed_channels in config.toml.\n'
            f"Only clip videos you made or have permission to clip. If you do have permission, either add\n"
            f'the channel to allowed_channels, or re-run with  --permission "how you got permission"\n'
            f'(e.g. --permission "Whop campaign: GTA6 clips, Nov 2026"). The note is saved next to the clips.'
        )

    download_dir = Path(cfg["download_dir"]).expanduser().resolve()
    download_dir.mkdir(parents=True, exist_ok=True)
    h = int(src_cfg.get("max_height", 1080))
    opts.update({
        "format": f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/bv*[height<={h}]+ba/b[height<={h}]/b",
        "merge_output_format": "mp4",
        "outtmpl": str(download_dir / "%(id)s.%(ext)s"),
    })
    print(f"Downloading: {info.get('title')}  ({channel})")
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
    if not path.exists():
        candidates = sorted(download_dir.glob(f"{info['id']}.*"))
        if not candidates:
            raise RuntimeError(f"Download finished but no file found for {url}")
        path = candidates[0]

    return Source(
        path=path, title=info.get("title") or info["id"], own=False, url=url, channel=channel,
        channel_url=info.get("channel_url") or info.get("uploader_url"),
        permission_note=permission_note or "listed in allowed_channels", heatmap=info.get("heatmap"),
    )
