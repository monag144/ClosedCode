from pathlib import Path
import importlib.util, os, tempfile
r=Path(__file__).resolve().parents[3]; bp=r/"scripts/closedcode/passthrough_server.py"; b=bp.read_text(); m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text()
for q in ["VERSION = \"0.8.19\"","HISTORY_LOCK = threading.RLock()","persist_messages(session_id, current_history_messages)","active_stream_register(request_id, None, session_id)","persist_timeline_items(session_id","conversation = [system] + prior_history + current_history_messages"]: assert q in b,q
assert "current_timeline" not in b
assert 'addMessageBubble("user", text);\n                toolStatus.setText(requestId.equals(activeProviderRequestId)' in m
sp=importlib.util.spec_from_file_location("ccdur",bp); mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as d:
 os.environ["CLOSEDCODE_PASSTHROUGH_HISTORY"]=d
 sid="op469-session"; rid="op469-request"
 mod.persist_messages(sid,[{"role":"user","content":"Initial"}])
 mod.active_stream_register(rid,None,sid)
 assert mod.active_stream_steer(rid,"Hello")
 assert mod.load_history(sid)==[{"role":"user","content":"Initial"},{"role":"user","content":"Hello"}]
 assert mod.load_timeline(sid)==[{"kind":"message","role":"user","content":"Initial"},{"kind":"message","role":"user","content":"Hello"}]
 assert mod.active_stream_take_steering(rid)==["Hello"]
 assert [q["content"] for q in mod.load_history(sid)]==["Initial","Hello"]
 mod.persist_timeline_items(sid,[{"kind":"tool","name":"shell","status":"completed","detail":"ok"}])
 mod.persist_messages(sid,[{"role":"assistant","content":"Done"}])
 assert [q.get("content",q.get("name")) for q in mod.load_timeline(sid)]==["Initial","Hello","shell","Done"]
 mod.active_stream_unregister(rid)
print("STEERING_DURABILITY_REGRESSION_GREEN")
