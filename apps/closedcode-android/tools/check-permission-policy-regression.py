from pathlib import Path
r=Path(__file__).resolve().parents[3]
m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text(); x=(r/"apps/closedcode-android/res/layout/activity_main.xml").read_text(); b=(r/"scripts/closedcode/passthrough_server.py").read_text()
for q in ["Approve all for this task","Always allow this tool in this workspace","Always allow this exact command","isWorkspaceScopedApprovalTool","approvalWorkspaceKey","legacyAgentApprovalKey","agentAlwaysAllowedActions","approveAllAgentRequests.contains(requestId)","isAgentActionAlwaysAllowed(name, arguments)",'optBoolean("resolved",false)','Permission expired']:
 assert q in m,q
assert 'timeout_seconds: int = 600' in b and 'VERSION = "0.8.19"' in b
assert 'YOLO_AUTO_APPROVAL_TOOLS' in b and '"shell"' not in b.split('YOLO_AUTO_APPROVAL_TOOLS = ',1)[1].split('\n',1)[0]
assert 'autonomy == "full" or (autonomy == "yolo" and name in YOLO_AUTO_APPROVAL_TOOLS)' in b
assert 'YOLO/FULL DANGER ACCESS' not in b and 'YOLO / Full Danger Access' not in x
assert 'YOLO / Auto-approve' in x and 'Shell still asks. This is not Full Access.' in x
print("PERMISSION_POLICY_REGRESSION_GREEN")
