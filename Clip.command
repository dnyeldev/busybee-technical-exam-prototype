#!/usr/bin/env bash
# Double-click me in Finder. Paste a URL or drag a video file into this window, press Enter.
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/gta6clip ]]; then
  echo "First run: setting things up (takes a few minutes)..."
  ./setup.sh || { read -r -p "Setup failed. Press Enter to close."; exit 1; }
fi
.venv/bin/pip install -q -U yt-dlp >/dev/null 2>&1 || true   # YouTube changes often; keep yt-dlp fresh

echo
echo "Paste a YouTube/Twitch URL or drag a video file here, then press Enter:"
read -r INPUT
INPUT="${INPUT%\"}"; INPUT="${INPUT#\"}"; INPUT="${INPUT%\'}"; INPUT="${INPUT#\'}"
INPUT="$(echo "$INPUT" | sed 's/\\ / /g; s/[[:space:]]*$//')"

PERM=()
if [[ "$INPUT" =~ ^https?:// ]]; then
  echo "If this creator isn't in allowed_channels, how did you get permission? (Enter to skip)"
  read -r NOTE
  [[ -n "$NOTE" ]] && PERM=(--permission "$NOTE")
fi

.venv/bin/gta6clip run "$INPUT" "${PERM[@]}"
open clips 2>/dev/null || true
read -r -p "Finished. Press Enter to close."
