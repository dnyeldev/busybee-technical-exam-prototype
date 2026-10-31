#!/usr/bin/env bash
# One-time setup for macOS. Run:  ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v brew >/dev/null 2>&1; then
  echo "Installing Homebrew (Mac package manager)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi

echo "Installing ffmpeg and Python..."
brew install ffmpeg python@3.12

PY="$(brew --prefix python@3.12)/bin/python3.12"
"$PY" -m venv .venv
.venv/bin/pip install --upgrade pip -q

if [[ "$(uname -m)" == "arm64" ]]; then
  echo "Apple Silicon detected: installing GPU speech-to-text (mlx-whisper)..."
  .venv/bin/pip install -q -e ".[mlx]"
else
  echo "Intel Mac detected: installing CPU speech-to-text (faster-whisper)..."
  .venv/bin/pip install -q -e ".[cpu]"
fi

[[ -f config.toml ]] || cp config.example.toml config.toml
chmod +x Clip.command

echo
.venv/bin/gta6clip doctor
echo
echo "Done. Double-click Clip.command, or run:  .venv/bin/gta6clip run <file-or-url>"
