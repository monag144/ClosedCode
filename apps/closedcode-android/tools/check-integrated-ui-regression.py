#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]; m=(r/'src/com/monag/closedcode/mobile/MainActivity.java').read_text(); x=(r/'AndroidManifest.xml').read_text()
def q(v,s):
 if not v: raise SystemExit('UI_RED:'+s)
q('POST_NOTIFICATIONS' in x,'permission'); q('signalCompletion(' in m,'alert'); q('!cancelled && !providerRunHadError' in m,'success-guard'); q('handleCompletionIntent' in m,'return'); q('optJSONArray("timeline")' in m,'timeline'); q('readableToolActivity' in m and 'Technical: ⚙ ' in m,'progress'); q(m.count('streamAgentPrompt(')==1,'provider-calls'); print('INTEGRATED_UI_GREEN')
