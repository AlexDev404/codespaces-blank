#!/usr/bin/env bash
# Idempotent setup: installs MuseScore 3 (apt) + xvfb, a venv with Pillow (image cropping only),
# and smoke-tests the CLI.
# The MuseScore 4 AppImage route is blocked by the network policy
# (api.github.com/repos/musescore/MuseScore -> 403 from the agent proxy).
set -euo pipefail
SUDO=""; if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null; then SUDO=sudo; fi

if command -v musescore3 >/dev/null && command -v xvfb-run >/dev/null; then
  echo "[setup] musescore3 and xvfb already installed - skipping apt"
else
  echo "[setup] installing musescore3 xvfb via apt"
  $SUDO apt-get update -qq
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq musescore3 xvfb
fi

if [ -x .venv/bin/python ]; then
  echo "[setup] .venv already present"
else
  echo "[setup] creating .venv with pillow"
  python3 -m venv .venv && .venv/bin/pip install -q pillow
fi

export QT_QPA_PLATFORM=offscreen
echo "[setup] smoke test:"
musescore3 --version 2>&1 | grep -v XDG || xvfb-run -a musescore3 --version
echo "[setup] done"
