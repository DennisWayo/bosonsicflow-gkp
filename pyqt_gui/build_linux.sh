#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bosonicflow-gkp"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
  else
    echo "Python not found. Activate your env or set PYTHON_BIN." >&2
    exit 1
  fi
fi

if ! "$PYTHON_BIN" -m PyInstaller --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install pyinstaller
fi

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --windowed \
  --name "$APP_NAME" \
  --collect-submodules pennylane \
  main.py

mkdir -p downloads
rm -f "downloads/${APP_NAME}-linux.zip"
cd downloads
zip -r "${APP_NAME}-linux.zip" "../dist/${APP_NAME}"
