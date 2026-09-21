from pathlib import Path
r=Path(__file__).resolve().parents[3]; m=(r/'apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java').read_text(); x=(r/'apps/closedcode-android/res/layout/activity_main.xml').read_text(); s=(r/'apps/closedcode-android/res/values/styles.xml').read_text()
for q in ['Theme_ClosedCode_Light','Theme_ClosedCode_ChocolateMint','appTheme','showThemePicker()','Chocolate Mint']: assert q in m,q
for q in ['android:id="@+id/themeRow"','android:id="@+id/themeValue"','APPEARANCE']: assert q in x,q
for q in ['Theme.ClosedCode.Light','Theme.ClosedCode.ChocolateMint','ccAccent','ccBg']: assert q in s,q
for name in ['cc_bg','cc_surface','cc_surface_2','cc_border','cc_text','cc_muted','cc_accent','cc_good','cc_bad']: assert (r/'apps/closedcode-android/res/color'/(name+'.xml')).exists(),name
print('THEME_REGRESSION_GREEN')
