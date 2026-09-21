from pathlib import Path
r=Path(__file__).resolve().parents[3]
s=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/OpenCodeSheet.java").read_text()
for q in ["MotionEvent.ACTION_DOWN","MotionEvent.ACTION_MOVE","MotionEvent.ACTION_UP","dismissThreshold","dialog::dismiss","0.94f","translationY(0f)","Drag sheet up to expand or down to close","attachSheetDrag(activity, dialog, content, window, heightFraction)"]:
 assert q in s,q
assert "present(activity, dialog, root, trigger, 0.78f, null);" in s
print("SHEET_DRAG_REGRESSION_GREEN")
