#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

PORT="${PORT:-8081}"
HOST="${HOST:-0.0.0.0}"

echo "=========================================================="
echo " Starting Calendar Social Media Harness on http://localhost:${PORT}"
echo "=========================================================="

export PYTHONPATH=.
if [ -f "$DIR/.venv/bin/python" ]; then
    exec "$DIR/.venv/bin/python" -m app.main
else
    exec python3 -m app.main
fi


