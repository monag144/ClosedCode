from pathlib import Path
r=Path(__file__).resolve().parents[3]
m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text(); b=(r/"scripts/closedcode/passthrough_server.py").read_text()
for x in ["Approve all for this task","Always allow this exact action","agentAlwaysAllowedActions","approveAllAgentRequests.contains(requestId)","isAgentActionAlwaysAllowed(name, arguments)",'optBoolean("resolved",false)','Permission expired']:
 assert x in m,x
assert 'timeout_seconds: int = 600' in b and 'VERSION = "0.8.16"' in b
print("PERMISSION_POLICY_REGRESSION_GREEN")
