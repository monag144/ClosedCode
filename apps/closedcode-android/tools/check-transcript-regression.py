#!/usr/bin/env python3
from pathlib import Path
import re
main=Path(__file__).resolve().parents[1]/'src/com/monag/closedcode/mobile/MainActivity.java'
s=main.read_text(encoding='utf-8')

def need(ok,msg):
    if not ok: raise SystemExit('TRANSCRIPT_REGRESSION_RED: '+msg)
def section(a,b):
    i=s.find(a); j=s.find(b,i+1)
    need(i>=0 and j>i,'section missing '+a)
    return s[i:j]

send=section('    private void sendPrompt() {','    private void dispatchPrompt(')
dispatch=section('    private void dispatchPrompt(','    private static boolean isPassthroughProvider')
stream=section('    private void dispatchPassthroughPrompt(','    private void showAgentPermission(')
abort=section('    private void abortPrompt() {','    private void setPromptRunning(')
lifecycle=section('    private void cancelActiveProviderForLifecycle() {','    private void animateBackToSessions()')
render=section('    private void renderMessages(String body) {','    private void addMessageBubble(')

need('private boolean passthroughSendActive;' in s,'guard field missing')
need('if (currentSessionId == null || passthroughSendActive) return;' in s,'loadMessages guard missing')
need(send.index('if (passthroughPrompt) passthroughSendActive = true;') < send.index('addMessageBubble("user", text);'),'guard acquired after optimistic user card')
need('passthroughSendActive = true;' not in dispatch,'late guard remains')
prefix=stream.split('api.streamAgentPrompt(',1)[0]
need('providerStreamBody = null;' in prefix,'stream body not initialized null')
need('providerStreamBody = addProviderStreamingBubble();' not in prefix,'assistant card eagerly reserved')
need('if (providerStreamBody == null)' in stream and 'providerStreamBody = addProviderStreamingBubble();' in stream,'assistant card not lazily created')
need('if (!cancelled) loadMessages();' not in stream,'completion still rebuilds transcript')
err=re.search(r'@Override public void error\(String message\) \{(.+?)\n\s*\}',stream,re.S)
need(err is not None,'error callback missing')
need('activeProviderRequestId = null' not in err.group(1),'in-band error tears down request')
need('passthroughSendActive = false' not in err.group(1),'in-band error releases guard')
need('passthroughSendActive = false;' not in abort.split('api.abort(',1)[0],'cancel request releases guard before terminal')
need(stream.count('passthroughSendActive = false;') >= 2,'terminal cleanup missing')
need('passthroughSendActive = false;' in lifecycle,'lifecycle cleanup missing')
need('if (passthroughSendActive)' in render,'render defense guard missing')
print('TRANSCRIPT_REGRESSION_GREEN')
