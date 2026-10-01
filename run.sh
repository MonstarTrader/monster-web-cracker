#!/usr/bin/env bash
# monster web cracker — unix launcher
# author: MR HAXOR
set -e
cd "$(dirname "$0")"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done

if [ -z "$PY" ]; then
  echo "!! python not found. run ./install.sh"
  exit 1
fi

exec "$PY" mwc.py "$@"
