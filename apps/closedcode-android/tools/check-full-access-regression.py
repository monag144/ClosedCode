from pathlib import Path
import importlib.util,tempfile
r=Path(__file__).resolve().parents[3];bp=r/"scripts/closedcode/passthrough_server.py";b=bp.read_text();m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text();x=(r/"apps/closedcode-android/res/layout/activity_main.xml").read_text()
for q in ['VERSION = "0.8.19"','{"ask", "yolo", "full"}','autonomy == "full"','full_access=autonomy == "full"','FULL ACCESS / DANGER']:assert q in b,q
for q in ['fullAccessAutonomy','fullAccessSwitch','bindAutonomyControls()','Enable Full Access?','? "full" :']:assert q in m,q
assert 'FULL ACCESS / Danger' in x and 'Off by default.' in x
sp=importlib.util.spec_from_file_location("f",bp);z=importlib.util.module_from_spec(sp);sp.loader.exec_module(z)
with tempfile.TemporaryDirectory() as d:
 a=Path(d);w=a/"w";o=a/"o";w.mkdir();o.mkdir();f=o/"x"
 try:z.agent_tool_result(str(w),"workspace_write",{"path":str(f),"content":"x"});raise AssertionError
 except ValueError:pass
 z.agent_tool_result(str(w),"workspace_write",{"path":str(f),"content":"x"},full_access=True);assert f.read_text()=="x"
 assert z.agent_tool_result(str(w),"shell",{"command":"pwd","cwd":str(o)},full_access=True)["stdout"].strip()==str(o.resolve())
 z.agent_tool_result(str(w),"workspace_delete",{"path":str(f)},full_access=True);assert not f.exists()
print("FULL_ACCESS_REGRESSION_GREEN")
