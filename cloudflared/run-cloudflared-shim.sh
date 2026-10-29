#!/usr/bin/env bash
set -euo pipefail
S="$(dirname "$0")"
python3 -I "$S/edge-shim.py" &
SHIM=$!
trap 'kill $SHIM 2>/dev/null' EXIT
sleep 1
cloudflared tunnel --no-autoupdate --protocol http2 --edge 127.0.0.1:7844 \
  run --token "$(cat /etc/cloudflared/token)"
