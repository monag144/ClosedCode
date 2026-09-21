from pathlib import Path
r=Path(__file__).resolve().parents[3]
m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text(); c=(r/"apps/closedcode-android/res/values/colors.xml").read_text()
for q in ["queueAgentPermission(","showPendingAgentPermissionIfAny()","finishInteractionDialog()","Approve all for this task","Always allow this tool in this workspace","Always allow this exact command","agentPermissionButton(","deleteLp.gravity = Gravity.END","ViewGroup.LayoutParams.WRAP_CONTENT"]: assert q in m,q
assert '.setMessage(detail).setItems' not in m
assert 'if (interactionDialogOpen) {\n            toast("Finish the current interaction first")' in m
assert '<color name="cc_dark_bg">#000000</color>' in c
assert '<color name="cc_dark_text">#FFFFFF</color>' in c
assert '<color name="cc_dark_muted">#F2F2F2</color>' in c
print("DEVICE_INTERACTION_REGRESSION_GREEN")
