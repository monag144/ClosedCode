#!/data/data/com.termux/files/usr/bin/sh
set -eu
umask 077
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
STATE_DIR="${CLOSEDCODE_STATE_DIR:-$HOME/.local/state/closedcode}"
PORT="${CLOSEDCODE_PASSTHROUGH_PORT:-4097}"
PID_FILE="$STATE_DIR/passthrough.pid"
LOG_FILE="$STATE_DIR/passthrough.log"
HEALTH="http://127.0.0.1:$PORT/health"
mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"

if curl -fsS --max-time 2 "$HEALTH" >/dev/null 2>&1; then
  echo "PASSTHROUGH_STATUS=ALREADY_HEALTHY"
  curl -fsS --max-time 2 "$HEALTH"
  echo
  exit 0
fi

if python - "$PORT" <<'PY'
import socket,sys
s=socket.socket(); s.settimeout(.4)
try: rc=s.connect_ex(("127.0.0.1",int(sys.argv[1])))
finally: s.close()
raise SystemExit(0 if rc == 0 else 1)
PY
then
  echo "PASSTHROUGH_STATUS=PORT_OCCUPIED_UNHEALTHY"
  exit 20
fi

nohup "$SCRIPT_DIR/run-passthrough.sh" >>"$LOG_FILE" 2>&1 &
PID=$!
printf '%s\n' "$PID" > "$PID_FILE"
chmod 600 "$PID_FILE"
i=0
while [ "$i" -lt 20 ]; do
  if curl -fsS --max-time 2 "$HEALTH" >/dev/null 2>&1; then
    echo "PASSTHROUGH_STATUS=STARTED"
    echo "PASSTHROUGH_PID=$PID"
    echo "PASSTHROUGH_LOG=$LOG_FILE"
    curl -fsS --max-time 2 "$HEALTH"
    echo
    exit 0
  fi
  i=$((i+1))
  sleep .25
done
kill "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true
echo "PASSTHROUGH_STATUS=START_FAILED"
exit 21
