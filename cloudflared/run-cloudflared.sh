#!/usr/bin/env bash
set -euo pipefail

TOKEN_FILE=/etc/cloudflared/token
if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "ERROR: token file not found at $TOKEN_FILE" >&2
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")
exec cloudflared tunnel --no-autoupdate run --token "$TOKEN"
