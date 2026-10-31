"""Command line: gta6clip run | watch | doctor."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from . import config
from .pipeline import Pipeline
from .sources import PermissionNotRecorded

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}


def _apply_overrides(cfg: dict, args: argparse.Namespace) -> dict:
    if getattr(args, "shorts", None) is not None:
        cfg["shorts"]["count"] = args.shorts
    if getattr(args, "no_shorts", False):
        cfg["shorts"]["enabled"] = False
    if getattr(args, "no_longform", False):
        cfg["longform"]["enabled"] = False
    if getattr(args, "no_captions", False):
        cfg["captions"]["enabled"] = False
    if getattr(args, "deep", False):
        cfg["detect"]["deep"] = True
    if getattr(args, "layout", None):
        cfg["shorts"]["layout"] = args.layout
    if getattr(args, "out", None):
        cfg["output_dir"] = args.out
    return cfg


def _inputs(args: argparse.Namespace) -> list[str]:
    items = list(args.inputs)
    if args.from_file:
        for line in Path(args.from_file).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line)
    return items


def cmd_run(args: argparse.Namespace) -> int:
    cfg = _apply_overrides(config.load(args.config), args)
    pipe = Pipeline(cfg)
    inputs = _inputs(args)
    if not inputs:
        print("Give me a video file or URL, e.g.  gta6clip run ~/Movies/gta6-session.mp4")
        return 2
    failures = 0
    for item in inputs:
        try:
            pipe.run(item, args.permission)
        except PermissionNotRecorded as exc:
            print(f"\nSkipped: {exc}\n", file=sys.stderr)
            failures += 1
        except Exception as exc:  # keep going through a batch
            print(f"\nFailed on {item}: {exc}\n", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


def _stable(path: Path, wait: float = 5.0) -> bool:
    """A recording that's still being written keeps growing; only take finished files."""
    size = path.stat().st_size
    time.sleep(wait)
    return path.exists() and path.stat().st_size == size and size > 0


def cmd_watch(args: argparse.Namespace) -> int:
    cfg = _apply_overrides(config.load(args.config), args)
    folder = Path(args.folder).expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    ledger = folder / ".gta6clip-done.json"
    done: set[str] = set(json.loads(ledger.read_text())) if ledger.exists() else set()
    pipe = Pipeline(cfg)
    print(f"Watching {folder} for new recordings (Ctrl+C to stop)...")
    try:
        while True:
            for f in sorted(folder.iterdir()):
                if f.suffix.lower() not in VIDEO_EXTS or f.name in done or f.name.startswith("."):
                    continue
                if not _stable(f):
                    continue
                try:
                    pipe.run(str(f))
                except Exception as exc:
                    print(f"Failed on {f.name}: {exc}", file=sys.stderr)
                done.add(f.name)
                ledger.write_text(json.dumps(sorted(done)))
            if args.once:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    import importlib.util
    import subprocess

    ok = True

    def check(label: str, passed: bool, fix: str = "") -> None:
        nonlocal ok
        ok &= passed
        print(f"  [{'ok' if passed else '!!'}] {label}" + ("" if passed else f"  ->  {fix}"))

    print("gta6clip doctor")
    has_ff = shutil.which("ffmpeg") is not None
    check("ffmpeg installed", has_ff, "brew install ffmpeg")
    if has_ff:
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        check("ffmpeg can burn captions (libass)", " ass " in filters, "brew reinstall ffmpeg")
        encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        hw = "h264_videotoolbox" in encoders
        print(f"  [{'ok' if hw else '--'}] Mac hardware encoder {'available (fast)' if hw else 'not found, using libx264'}")
    check("yt-dlp installed", importlib.util.find_spec("yt_dlp") is not None, "./setup.sh")
    engines = [m for m in ("mlx_whisper", "faster_whisper") if importlib.util.find_spec(m)]
    check("speech-to-text engine (" + (", ".join(engines) or "none") + ")", bool(engines), "./setup.sh")
    print("All good." if ok else "Fix the items marked !! and run doctor again.")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gta6clip", description="Automatic GTA 6 highlight clipper.")
    p.add_argument("--config", help="path to config.toml (default: ./config.toml if it exists)")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--shorts", type=int, help="number of vertical clips to make")
        sp.add_argument("--no-shorts", action="store_true", help="skip vertical clips")
        sp.add_argument("--no-longform", action="store_true", help="skip the 16:9 compilation")
        sp.add_argument("--no-captions", action="store_true", help="skip speech-to-text captions")
        sp.add_argument("--deep", action="store_true", help="transcribe everything for better picks (slower)")
        sp.add_argument("--layout", choices=["blur", "crop"], help="vertical layout")
        sp.add_argument("--out", help="output folder (default: ./clips)")

    run = sub.add_parser("run", help="clip one or more files / URLs")
    run.add_argument("inputs", nargs="*", help="video files or URLs")
    run.add_argument("--from-file", help="text file with one file path or URL per line")
    run.add_argument("--permission", help='how you got permission to clip a creator, e.g. "Whop campaign X"')
    common(run)
    run.set_defaults(func=cmd_run)

    watch = sub.add_parser("watch", help="auto-clip every new recording dropped in a folder")
    watch.add_argument("folder")
    watch.add_argument("--interval", type=float, default=30, help="seconds between checks")
    watch.add_argument("--once", action="store_true", help="process what's there now, then exit")
    common(watch)
    watch.set_defaults(func=cmd_watch)

    doctor = sub.add_parser("doctor", help="check that everything is installed")
    doctor.set_defaults(func=cmd_doctor)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 2
