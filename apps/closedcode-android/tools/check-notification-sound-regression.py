from pathlib import Path
r=Path(__file__).resolve().parents[3]
m=(r/"apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java").read_text(); x=(r/"apps/closedcode-android/res/layout/activity_main.xml").read_text()
for q in ["completionSoundToggle","completionSoundChoose","completionSoundTest","ACTION_RINGTONE_PICKER","completionSoundEnabled","ERROR_CHANNEL_ID","signalError(requestId",'("complete|"+sid+"|"+rid).hashCode()','("error|"+sid+"|"+rid).hashCode()',"notifyErrors"]:
 assert q in m or q in x,q
assert 'android:id="@+id/completionSoundRow"' in x
assert 'android:id="@+id/completionSoundToggle"' in x
assert 'android:id="@+id/completionSoundChoose"' in x
assert 'android:id="@+id/completionSoundTest"' in x
assert 'nm.notify(sid.hashCode(),n)' not in m
print("NOTIFICATION_SOUND_REGRESSION_GREEN")
