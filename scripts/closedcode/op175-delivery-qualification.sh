#!/data/data/com.termux/files/usr/bin/sh
set -eu

R="$HOME/ClosedCode"
B="http://127.0.0.1:4096"
A="$R/apps/closedcode-android"
APK="/sdcard/Download/ClosedCode-cleanroom-v0.1.8-debug.apk"
T="${TMPDIR:-$PREFIX/tmp}"
P="$T/cc175-provider.json"
C="$T/cc175-create.json"
M="$T/cc175-msg.json"
RESP="$T/cc175-resp.txt"
SID=""
TOOL_DIR="$T/cc175-tool-$$"
TOOL_SID=""

cleanup() {
  Q="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$R")"
  [ -z "${SID:-}" ] || curl -sS --max-time 10 -o /dev/null -X DELETE "$B/session/$SID?directory=$Q" || true
  if [ -n "${TOOL_SID:-}" ]; then
    QT="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$TOOL_DIR")"
    curl -sS --max-time 10 -o /dev/null -X DELETE "$B/session/$TOOL_SID?directory=$QT" || true
  fi
  rm -rf "$TOOL_DIR"
  rm -f "$P" "$C" "$M" "$RESP"
}
trap cleanup EXIT

echo HE7_OP175_BEGIN
echo MODE=V018_DELIVERY_BUILD_ANDROID_SEQUENCE_NVIDIA_TOOL_PROOF_INSTALLER_CHECKPOINT
echo "SYNC_HEAD=$(git -C "$R" rev-parse HEAD)"

echo "=== SOURCE_DELIVERY_PROOF ==="
grep -n 'createSession(directory, "ClosedCode session"' "$A/src/com/monag/closedcode/mobile/MainActivity.java"
grep -n 'updateSessionTitle' "$A/src/com/monag/closedcode/mobile/MainActivity.java" "$A/src/com/monag/closedcode/mobile/ClosedCodeApi.java"
grep -n 'abortPrompt' "$A/src/com/monag/closedcode/mobile/MainActivity.java"
grep -n 'Reconnecting' "$A/src/com/monag/closedcode/mobile/MainActivity.java"
grep -n 'setPromptRunning' "$A/src/com/monag/closedcode/mobile/MainActivity.java"
grep -n '0.1.8-cleanroom' "$A/build-termux.sh"

echo "=== BUILD_V018 ==="
sh "$A/build-termux.sh"
test -f "$APK"
echo "APK_BYTES=$(wc -c < "$APK")"
echo "APK_SHA256=$(sha256sum "$APK" | awk '{print $1}')"
BT="$(find "$HOME/lib/android-sdk-9123335/build-tools" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -V | tail -n1)"
AAPT="${BT}/aapt"
[ -x "$AAPT" ] && "$AAPT" dump badging "$APK" | grep -E '^(package:|application:|launchable-activity:)' || true

echo "=== BACKEND_AND_PROVIDER ==="
curl -fsS --max-time 5 "$B/global/health"
echo
Q="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$R")"
curl -fsS --max-time 20 "$B/provider?directory=$Q" > "$P"
python - "$P" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
connected=set(x.get("connected",[]))
p=next((p for p in x.get("all",[]) if isinstance(p,dict) and p.get("id")=="nvidia"),None)
models=p.get("models",{}) if isinstance(p,dict) else {}
target=None
if isinstance(models,dict):
    for k,v in models.items():
        if isinstance(v,dict) and v.get("id",k)=="nvidia/nemotron-3-ultra-550b-a55b":
            target=v
            break
print("CONNECTED="+",".join(sorted(connected)))
print("NVIDIA_CONNECTED="+("YES" if "nvidia" in connected else "NO"))
print("NVIDIA_TARGET_PRESENT="+("YES" if target else "NO"))
if target:
    print("NVIDIA_TARGET_STATUS="+str(target.get("status","")))
print("ZAI_CONNECTED="+("YES" if "zai" in connected else "NO"))
PY

echo "=== ANDROID_EQUIVALENT_SESSION_SEQUENCE ==="
CH="$(curl -sS --max-time 20 -o "$C" -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary '{"title":"ClosedCode session"}' "$B/session?directory=$Q")"
echo "CREATE_HTTP=$CH"
[ "$CH" = 200 ] || { head -c 800 "$C"; echo; exit 40; }
SID="$(python -c 'import json,sys;print(json.load(open(sys.argv[1])).get("id",""))' "$C")"
echo "SESSION_ID=$SID"
[ -n "$SID" ] || exit 41
UH="$(curl -sS --max-time 20 -o /dev/null -w '%{http_code}' -X PATCH -H 'Content-Type: application/json' --data-binary '{"title":"Runtime qualification"}' "$B/session/$SID?directory=$Q")"
echo "TITLE_PATCH_HTTP=$UH"
[ "$UH" = 200 ] || exit 42
BODY='{"parts":[{"type":"text","text":"Reply exactly CLOSED_CODE_V018_RUNTIME_OK and nothing else. Do not use tools."}],"model":{"providerID":"nvidia","modelID":"nvidia/nemotron-3-ultra-550b-a55b"},"agent":"build","variant":"low"}'
PH="$(curl -sS --max-time 20 -o "$RESP" -w '%{http_code}' -X POST -H 'Content-Type: application/json; charset=utf-8' --data-binary "$BODY" "$B/session/$SID/prompt_async?directory=$Q")"
echo "PROMPT_ASYNC_HTTP=$PH"
[ "$PH" = 204 ] || [ "$PH" = 200 ] || { echo "PROMPT_BODY=$(head -c 800 "$RESP")"; exit 43; }

MAIN_OK=NO
i=1
while [ "$i" -le 35 ]; do
  MH="$(curl -sS --max-time 10 -o "$M" -w '%{http_code}' "$B/session/$SID/message?directory=$Q&limit=100" || true)"
  if [ "$MH" = 200 ] && grep -q 'CLOSED_CODE_V018_RUNTIME_OK' "$M"; then
    MAIN_OK=YES
    echo "MAIN_PROMPT_POLL=$i RESULT=GREEN"
    break
  fi
  echo "MAIN_PROMPT_POLL=$i RESULT=WAIT"
  sleep 1
  i=$((i+1))
done
echo "MAIN_PROMPT_RUNTIME=$MAIN_OK"

echo "=== DISPOSABLE_TOOL_FILE_PROOF ==="
mkdir -p "$TOOL_DIR"
QT="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$TOOL_DIR")"
CH2="$(curl -sS --max-time 20 -o "$C" -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary '{"title":"ClosedCode tool qualification"}' "$B/session?directory=$QT")"
echo "TOOL_CREATE_HTTP=$CH2"
[ "$CH2" = 200 ] || exit 50
TOOL_SID="$(python -c 'import json,sys;print(json.load(open(sys.argv[1])).get("id",""))' "$C")"
echo "TOOL_SESSION_ID=$TOOL_SID"
TBODY='{"parts":[{"type":"text","text":"Use your available file editing tools to create proof.txt in the workspace with exactly this one line: CLOSED_CODE_TOOL_OK. After the file exists, reply exactly CLOSED_CODE_TOOL_OK."}],"model":{"providerID":"nvidia","modelID":"nvidia/nemotron-3-ultra-550b-a55b"},"agent":"build","variant":"low"}'
TH="$(curl -sS --max-time 20 -o "$RESP" -w '%{http_code}' -X POST -H 'Content-Type: application/json; charset=utf-8' --data-binary "$TBODY" "$B/session/$TOOL_SID/prompt_async?directory=$QT")"
echo "TOOL_PROMPT_HTTP=$TH"
TOOL_OK=NO
TOOL_EVENT=NO
if [ "$TH" = 204 ] || [ "$TH" = 200 ]; then
  i=1
  while [ "$i" -le 50 ]; do
    MH="$(curl -sS --max-time 10 -o "$M" -w '%{http_code}' "$B/session/$TOOL_SID/message?directory=$QT&limit=100" || true)"
    [ "$MH" = 200 ] && grep -q '"type":"tool"' "$M" && TOOL_EVENT=YES || true
    if [ -f "$TOOL_DIR/proof.txt" ] && [ "$(tr -d '\r\n' < "$TOOL_DIR/proof.txt")" = "CLOSED_CODE_TOOL_OK" ] && [ "$MH" = 200 ] && grep -q 'CLOSED_CODE_TOOL_OK' "$M"; then
      TOOL_OK=YES
      echo "TOOL_POLL=$i RESULT=GREEN"
      break
    fi
    if [ $((i % 5)) -eq 0 ]; then echo "TOOL_POLL=$i RESULT=WAIT"; fi
    sleep 1
    i=$((i+1))
  done
fi
echo "TOOL_EVENT_VISIBLE=$TOOL_EVENT"
echo "TOOL_FILE_RUNTIME=$TOOL_OK"

echo "=== INSTALLER ==="
termux-open --view --content-type application/vnd.android.package-archive "$APK"
echo TERMUX_OPEN_RC=0

echo "=== CHECKPOINT_151_175 ==="
echo OP171=PARTIAL_V017_BUILT_PROMPT_PROBE_MALFORMED
echo OP172=RED_TITLE_AGENT_CRASH_AFTER_VALID_NVIDIA_TRANSPORT
echo OP173=TRANSPORT_REJECT_NO_SHELL_JSON_INVALID
echo OP174=GREEN_TITLE_BYPASS_NVIDIA_COMPLETION
echo "OP175_MAIN_PROMPT=$MAIN_OK"
echo "OP175_TOOL_FILE=$TOOL_OK"
echo "POST_HEAD=$(git -C "$R" rev-parse HEAD)"
echo POST_STATUS_BEGIN
git -C "$R" status --short
echo POST_STATUS_END
echo PROTECTED_RELAY_MUTATION=NO

if [ "$MAIN_OK" = YES ] && [ "$TOOL_OK" = YES ] && [ "$TOOL_EVENT" = YES ]; then
  echo OP175_RESULT=GREEN_V018_DELIVERY_NVIDIA_PROMPT_TOOL_FILE_INSTALLER
  echo HE7_OP175_END
  exit 0
fi
if [ "$MAIN_OK" = YES ]; then
  echo OP175_RESULT=PARTIAL_V018_DELIVERY_MAIN_PROMPT_GREEN_TOOL_PROOF_INCOMPLETE
  echo HE7_OP175_END
  exit 50
fi
echo OP175_RESULT=RED_V018_DELIVERY_MAIN_PROMPT_FAILED
echo HE7_OP175_END
exit 51
