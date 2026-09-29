from pathlib import Path

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing marker: {label}")
    return text.replace(old, new, 1)

# Backend: native workspace diff endpoint and version bump.
server = Path("scripts/closedcode/passthrough_server.py")
s = server.read_text()
s = replace_once(s, 'VERSION = "0.8.0"', 'VERSION = "0.8.1"', "backend version")
s = replace_once(
    s,
    'if parsed.path in {"/fs/list", "/fs/read", "/fs/search"}:',
    'if parsed.path in {"/fs/list", "/fs/read", "/fs/search", "/fs/diff"}:',
    "GET fs route set",
)
marker = '''                root_value = (query.get("root") or [""])[0]
                if parsed.path == "/fs/list":
'''
insert = '''                root_value = (query.get("root") or [""])[0]
                if parsed.path == "/fs/diff":
                    status_result = agent_tool_result(root_value, "git_status", {})
                    diff_result = agent_tool_result(root_value, "git_diff", {})
                    self.send_json(
                        200,
                        {
                            "root": str(workspace_root(root_value)),
                            "status": status_result.get("output", ""),
                            "diff": diff_result.get("output", ""),
                            "statusTruncated": bool(status_result.get("truncated", False)),
                            "diffTruncated": bool(diff_result.get("truncated", False)),
                        },
                    )
                    return
                if parsed.path == "/fs/list":
'''
s = replace_once(s, marker, insert, "fs diff handler")
server.write_text(s)

# Android API: send autonomy mode and expose native workspace diff.
api = Path("apps/closedcode-android/src/com/monag/closedcode/mobile/ClosedCodeApi.java")
a = api.read_text()
old_sig = '''            String providerId,
            String modelId,
            String requestId,
            AgentStreamListener listener) {
'''
new_sig = '''            String providerId,
            String modelId,
            String autonomy,
            String requestId,
            AgentStreamListener listener) {
'''
a = replace_once(a, old_sig, new_sig, "streamAgentPrompt signature")
old_body = '''                body.put("providerID", providerId);
                body.put("model", modelId);
                body.put("sessionID", sessionId);
'''
new_body = '''                body.put("providerID", providerId);
                body.put("model", modelId);
                body.put("autonomy", autonomy == null ? "ask" : autonomy);
                body.put("sessionID", sessionId);
'''
a = replace_once(a, old_body, new_body, "agent autonomy body")
marker = '''    public void workspaceRead(String root, String path, Callback cb) {
'''
method = '''    public void workspaceDiff(String root, Callback cb) {
        asyncAbsolute(
                "GET",
                "http://127.0.0.1:4097/fs/diff?root=" + enc(root),
                null,
                cb);
    }

'''
a = replace_once(a, marker, method + marker, "workspaceDiff method")
api.write_text(a)

# MainActivity: persistent YOLO toggle, request wiring, native change-review routing.
main = Path("apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java")
m = main.read_text()
m = replace_once(
    m,
    '''    private Switch hidePreviewSwitch;
    private Switch permissionNotifySwitch;
''',
    '''    private Switch hidePreviewSwitch;
    private Switch yoloSwitch;
    private Switch permissionNotifySwitch;
''',
    "yolo field",
)
m = replace_once(
    m,
    '''        hidePreviewSwitch = findViewById(R.id.hidePreviewSwitch);
        permissionNotifySwitch = findViewById(R.id.permissionNotifySwitch);
''',
    '''        hidePreviewSwitch = findViewById(R.id.hidePreviewSwitch);
        yoloSwitch = findViewById(R.id.yoloSwitch);
        permissionNotifySwitch = findViewById(R.id.permissionNotifySwitch);
''',
    "yolo bind",
)
m = replace_once(
    m,
    '''        bindToggle(R.id.hidePreviewRow, hidePreviewSwitch, "hideAppPreview", false, true);
        bindToggle(R.id.permissionNotifyRow, permissionNotifySwitch, "notifyPermissions", true, false);
''',
    '''        bindToggle(R.id.hidePreviewRow, hidePreviewSwitch, "hideAppPreview", false, true);
        bindToggle(R.id.yoloRow, yoloSwitch, "yoloAutonomy", false, false);
        bindToggle(R.id.permissionNotifyRow, permissionNotifySwitch, "notifyPermissions", true, false);
''',
    "yolo toggle action",
)
m = replace_once(
    m,
    '''                providerId,
                modelId,
                requestId,
                new ClosedCodeApi.AgentStreamListener() {
''',
    '''                providerId,
                modelId,
                prefs.getBoolean("yoloAutonomy", false) ? "yolo" : "ask",
                requestId,
                new ClosedCodeApi.AgentStreamListener() {
''',
    "agent autonomy dispatch",
)
start = m.index("    private void showDiff() {")
end = m.index("\n    private void saveBackend()", start)
new_diff = '''    private void showDiff() {
        if (currentSessionId == null) return;
        final boolean nativeProvider = isPassthroughProvider(composerUi.providerId());
        ClosedCodeApi.Callback callback = new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                String pretty = body;
                if (nativeProvider) {
                    try {
                        JSONObject result = new JSONObject(body);
                        String status = result.optString("status", "");
                        String diff = result.optString("diff", "");
                        StringBuilder out = new StringBuilder();
                        if (!status.isEmpty()) out.append("status\\n").append(status);
                        if (!diff.isEmpty()) {
                            if (out.length() > 0) out.append("\\n");
                            out.append("diff\\n").append(diff);
                        }
                        if (result.optBoolean("statusTruncated", false)) out.append("\\n[status truncated]");
                        if (result.optBoolean("diffTruncated", false)) out.append("\\n[diff truncated]");
                        pretty = out.length() == 0 ? "No workspace changes." : out.toString();
                    } catch (Exception ignored) {}
                } else {
                    try { pretty = new JSONArray(body).toString(2); } catch (Exception ignored) {}
                }
                TextView text = simpleText(pretty, 12, R.color.cc_text);
                text.setTextIsSelectable(true);
                text.setPadding(dp(16), dp(10), dp(16), dp(10));
                ScrollView scroll = new ScrollView(MainActivity.this);
                scroll.setBackgroundColor(getColor(R.color.cc_bg));
                scroll.addView(text);
                new AlertDialog.Builder(MainActivity.this)
                        .setTitle(nativeProvider ? "Workspace changes" : "Session diff")
                        .setView(scroll)
                        .setPositiveButton("Done", null)
                        .show();
            }
            @Override public void failure(String message) { toast("Diff: " + message); }
        };
        if (nativeProvider) api.workspaceDiff(directory, callback);
        else api.diff(currentSessionId, directory, callback);
    }
'''
m = m[:start] + new_diff + m[end:]
main.write_text(m)

# Settings UI: explicit persisted YOLO switch, default remains ASK.
layout = Path("apps/closedcode-android/res/layout/activity_main.xml")
x = layout.read_text()
marker = '''                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="18dp"
                    android:text="NOTIFICATIONS"
'''
block = '''                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="18dp"
                    android:text="AGENT AUTONOMY"
                    android:textColor="@color/cc_muted"
                    android:textSize="11sp"
                    android:textStyle="bold" />

                <LinearLayout
                    android:id="@+id/yoloRow"
                    android:layout_width="match_parent"
                    android:layout_height="70dp"
                    android:clickable="true"
                    android:focusable="true"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">
                        <TextView
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:text="YOLO / Full Danger Access"
                            android:textColor="@color/cc_text"
                            android:textSize="15sp" />
                        <TextView
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:layout_marginTop="2dp"
                            android:text="Auto-approve ordinary project coding tools. Task scope still applies."
                            android:textColor="@color/cc_muted"
                            android:textSize="11sp" />
                    </LinearLayout>
                    <Switch
                        android:id="@+id/yoloSwitch"
                        android:layout_width="wrap_content"
                        android:layout_height="match_parent"
                        android:clickable="false"
                        android:focusable="false" />
                </LinearLayout>

'''
x = replace_once(x, marker, block + marker, "autonomy settings block")
layout.write_text(x)

# Android package version bump.
build = Path("apps/closedcode-android/build-termux.sh")
b = build.read_text()
b = replace_once(b, 'ClosedCode-cleanroom-v0.2.3-debug.apk', 'ClosedCode-cleanroom-v0.2.4-debug.apk', "apk name")
b = replace_once(b, '--version-code 15', '--version-code 16', "version code")
b = replace_once(b, '--version-name "0.2.3-cleanroom"', '--version-name "0.2.4-cleanroom"', "version name")
b = replace_once(b, 'VERSION_NAME=0.2.3-cleanroom', 'VERSION_NAME=0.2.4-cleanroom', "version echo")
build.write_text(b)

print("ANDROID_AUTONOMY_NATIVE_DIFF_PATCH=GREEN")
