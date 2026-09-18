#!/data/data/com.termux/files/usr/bin/sh
set -eu

R="$HOME/ClosedCode"
B="http://127.0.0.1:4096"
T="${TMPDIR:-$PREFIX/tmp}"
LOG="$HOME/.local/share/opencode/log/opencode.log"
P="$T/cc176-provider.json"
A="$T/cc176-agent.json"
OLD_SID="ses_f4ddbd413ffeWuzZNjGLsEaxas"

cleanup() {
  rm -f "$P" "$A"
}
trap cleanup EXIT

echo HE7_OP176_BEGIN
echo MODE=TOOL_RUNTIME_ISOLATION_NO_PRODUCT_MUTATION

echo "=== BACKEND_HEALTH ==="
curl -fsS --max-time 5 "$B/global/health"
echo

Q="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$R")"

echo "=== OP175_FAILED_TOOL_SESSION_LOG ==="
if [ -f "$LOG" ]; then
  grep -F "$OLD_SID" "$LOG" | tail -40 || true
else
  echo LOG_ABSENT
fi

echo "=== MODEL_CAPABILITY_METADATA ==="
curl -fsS --max-time 20 "$B/provider?directory=$Q" > "$P"
python - "$P" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
for provider_id, model_id in [
    ("nvidia","nvidia/nemotron-3-ultra-550b-a55b"),
    ("opencode","big-pickle"),
]:
    p=next((p for p in x.get("all",[]) if isinstance(p,dict) and p.get("id")==provider_id),None)
    models=p.get("models",{}) if isinstance(p,dict) else {}
    m=None
    if isinstance(models,dict):
        for k,v in models.items():
            if isinstance(v,dict) and v.get("id",k)==model_id:
                m=v; break
    print(f"MODEL={provider_id}/{model_id}")
    print("CONNECTED="+("YES" if provider_id in set(x.get("connected",[])) else "NO"))
    print("PRESENT="+("YES" if m else "NO"))
    if not isinstance(m,dict):
        continue
    print("NAME="+str(m.get("name","")))
    print("STATUS="+str(m.get("status","")))
    print("MODEL_KEYS="+",".join(sorted(m.keys())))
    for key in sorted(m):
        lk=key.lower()
        if any(w in lk for w in ("tool","capab","reason","attach","structur")):
            value=m.get(key)
            text=json.dumps(value,separators=(",",":")) if isinstance(value,(dict,list)) else str(value)
            print(f"META_{key}={text[:1000]}")
PY

echo "=== BUILD_AGENT_PERMISSION_METADATA ==="
curl -fsS --max-time 20 "$B/agent?directory=$Q" > "$A"
python - "$A" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
items=x if isinstance(x,list) else []
a=next((i for i in items if isinstance(i,dict) and i.get("name")=="build"),None)
print("BUILD_AGENT_PRESENT="+("YES" if a else "NO"))
if isinstance(a,dict):
    perms=a.get("permission",[])
    print("BUILD_AGENT_MODE="+str(a.get("mode","")))
    print("PERMISSION_RULE_COUNT="+str(len(perms) if isinstance(perms,list) else -1))
    if isinstance(perms,list):
        for r in perms:
            if not isinstance(r,dict): continue
            perm=str(r.get("permission",""))
            if perm in ("bash","edit","read","write","external_directory","question"):
                print("PERM|"+perm+"|"+str(r.get("pattern",""))+"|"+str(r.get("action","")))
PY

run_case() {
  LABEL="$1"
  PROVIDER="$2"
  MODEL="$3"
  VARIANT="$4"
  DIR="$T/cc176-$LABEL-$$"
  C="$T/cc176-$LABEL-create.json"
  M="$T/cc176-$LABEL-msg.json"
  RESP="$T/cc176-$LABEL-resp.txt"
  PERM="$T/cc176-$LABEL-perm.json"
  SID=""
  mkdir -p "$DIR"
  QD="$(python -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$DIR")"

  CH="$(curl -sS --max-time 20 -o "$C" -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary '{"title":"ClosedCode tool isolation"}' "$B/session?directory=$QD" || true)"
  echo "CASE=$LABEL CREATE_HTTP=$CH"
  if [ "$CH" != 200 ]; then
    head -c 800 "$C" 2>/dev/null || true
    echo
    rm -rf "$DIR" "$C" "$M" "$RESP" "$PERM"
    return
  fi
  SID="$(python -c 'import json,sys;print(json.load(open(sys.argv[1])).get("id",""))' "$C")"
  echo "CASE=$LABEL SESSION_ID=$SID"

  BODY="$(python - "$PROVIDER" "$MODEL" "$VARIANT" <<'PY'
import json,sys
provider,model,variant=sys.argv[1:4]
x={
 "parts":[{"type":"text","text":"You must use a tool. Use the bash tool to run exactly: printf 'CLOSED_CODE_TOOL_OK\\n' > proof.txt . Then use a tool to read proof.txt and reply exactly CLOSED_CODE_TOOL_OK. Do not merely describe the command."}],
 "model":{"providerID":provider,"modelID":model},
 "agent":"build",
}
if variant:
    x["variant"]=variant
print(json.dumps(x,separators=(",",":")))
PY
)"
  PH="$(curl -sS --max-time 20 -o "$RESP" -w '%{http_code}' -X POST -H 'Content-Type: application/json; charset=utf-8' --data-binary "$BODY" "$B/session/$SID/prompt_async?directory=$QD" || true)"
  echo "CASE=$LABEL PROMPT_HTTP=$PH"

  RESULT=WAIT
  i=1
  while [ "$i" -le 30 ]; do
    MH="$(curl -sS --max-time 10 -o "$M" -w '%{http_code}' "$B/session/$SID/message?directory=$QD&limit=100" || true)"
    curl -sS --max-time 10 -o "$PERM" "$B/permission?directory=$QD" || true
    RESULT="$(python - "$M" "$PERM" "$DIR/proof.txt" <<'PY'
import json,sys,os
mp,pp,fp=sys.argv[1:4]
try: msgs=json.load(open(mp))
except Exception: msgs=[]
try: perms=json.load(open(pp))
except Exception: perms=[]
tools=[]
errors=[]
texts=[]
for item in msgs if isinstance(msgs,list) else []:
    if not isinstance(item,dict): continue
    info=item.get("info") if isinstance(item.get("info"),dict) else {}
    if info.get("role")!="assistant": continue
    if info.get("error"): errors.append(str(info.get("error"))[:300].replace("\n"," "))
    for p in item.get("parts",[]) if isinstance(item.get("parts"),list) else []:
        if not isinstance(p,dict): continue
        if p.get("type")=="tool": tools.append(str(p.get("tool","")))
        if p.get("type")=="text" and p.get("text"): texts.append(str(p.get("text")))
file_ok=os.path.isfile(fp) and open(fp,errors="ignore").read().strip()=="CLOSED_CODE_TOOL_OK"
reply_ok="CLOSED_CODE_TOOL_OK" in "\n".join(texts)
perm_count=len(perms) if isinstance(perms,list) else -1
if file_ok and tools:
    status="GREEN"
elif errors:
    status="ERROR"
elif texts and not tools:
    status="TEXT_NO_TOOL"
else:
    status="WAIT"
print(f"{status}|tools={','.join(tools)}|file={'YES' if file_ok else 'NO'}|reply={'YES' if reply_ok else 'NO'}|permissions={perm_count}|error={(errors[-1] if errors else '')}")
PY
)"
    if [ $((i % 5)) -eq 0 ] || printf '%s' "$RESULT" | grep -Eq '^(GREEN|ERROR|TEXT_NO_TOOL)'; then
      echo "CASE=$LABEL POLL=$i RESULT=$RESULT"
    fi
    case "$RESULT" in
      GREEN*|ERROR*|TEXT_NO_TOOL*) break ;;
    esac
    sleep 1
    i=$((i+1))
  done

  echo "CASE=$LABEL FINAL=$RESULT"
  echo "CASE=$LABEL LOG_BEGIN"
  if [ -f "$LOG" ]; then grep -F "$SID" "$LOG" | tail -25 || true; fi
  echo "CASE=$LABEL LOG_END"

  curl -sS --max-time 10 -o /dev/null -X DELETE "$B/session/$SID?directory=$QD" || true
  rm -rf "$DIR" "$C" "$M" "$RESP" "$PERM"
}

echo "=== NVIDIA_TOOL_CASE ==="
run_case nvidia nvidia nvidia/nemotron-3-ultra-550b-a55b low

echo "=== OPENCODE_TOOL_CONTROL ==="
run_case opencode opencode big-pickle ""

echo "=== FINAL_STATE ==="
echo "HEAD=$(git -C "$R" rev-parse HEAD)"
echo STATUS_BEGIN
git -C "$R" status --short
echo STATUS_END
echo PROTECTED_RELAY_MUTATION=NO
echo OP176_RESULT=DIAGNOSTIC_COMPLETE
echo HE7_OP176_END
