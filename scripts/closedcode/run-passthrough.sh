#!/data/data/com.termux/files/usr/bin/sh
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PORT="${CLOSEDCODE_PASSTHROUGH_PORT:-4097}"
exec python "$SCRIPT_DIR/passthrough_server.py" --host 127.0.0.1 --port "$PORT"
