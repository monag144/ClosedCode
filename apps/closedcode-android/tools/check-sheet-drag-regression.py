from pathlib import Path
r=Path(__file__).resolve().parents[3]
s=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/OpenCodeSheet.java").read_text()
for q in [
 "LinearLayout dragSurface = new LinearLayout(activity)",
 "ViewGroup.LayoutParams.MATCH_PARENT",
 "dp(activity, 48)",
 "dragSurface.addView(handle, handleLp)",
 "View dragSurface = group.getChildAt(0)",
 "dragSurface.setOnTouchListener",
 "MotionEvent.ACTION_DOWN",
 "MotionEvent.ACTION_MOVE",
 "MotionEvent.ACTION_UP",
 "dismissThreshold",
 "dialog::dismiss",
 "0.94f",
 "translationY(0f)",
 "v.performClick()"
]: assert q in s,q
assert 'handle.setOnTouchListener' not in s
assert 'root.addView(handle, handleLp)' not in s
assert 'new LinearLayout.LayoutParams(dp(activity, 42), dp(activity, 4))' in s
assert 'present(activity, dialog, root, trigger, 0.78f, null);' in s
print("SHEET_DRAG_REGRESSION_GREEN")
