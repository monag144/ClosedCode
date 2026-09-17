package com.monag.closedcode.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public final class MainActivity extends Activity {
    private static final String PREFS = "closedcode.mobile";
    private static final String DEFAULT_URL = "http://127.0.0.1:4096";
    private static final String DEFAULT_DIRECTORY = "/data/data/com.termux/files/home/ClosedCode";

    private LinearLayout sessionsPage;
    private LinearLayout connectionsPage;
    private ScrollView settingsPage;
    private LinearLayout chatPage;
    private LinearLayout bottomNav;
    private LinearLayout sessionList;
    private LinearLayout messageList;
    private ScrollView messageScroll;

    private TextView navSessions;
    private TextView navConnections;
    private TextView navSettings;
    private TextView headerStatus;
    private TextView serverDot;
    private TextView serverState;
    private TextView serverSubtitle;
    private TextView workspacePath;
    private TextView connectionBadge;
    private TextView connectionUrl;
    private TextView connectionVersion;
    private TextView chatTitle;
    private TextView chatWorkspace;
    private TextView modelChip;
    private TextView toolStatus;
    private EditText composer;
    private EditText serverUrlInput;
    private EditText directoryInput;
    private Switch biometricSwitch;
    private Switch hidePreviewSwitch;
    private Switch permissionNotifySwitch;
    private Switch questionNotifySwitch;
    private Switch completedNotifySwitch;
    private Switch errorNotifySwitch;
    private boolean interactionDialogOpen;

    private SharedPreferences prefs;
    private ClosedCodeApi api;
    private String directory;
    private String currentSessionId;
    private boolean serverHealthy;
    private String lastVersion = "—";
    private String lastModelLabel = "backend default";
    private boolean requestDialogOpen;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.activity_main);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        directory = prefs.getString("directory", DEFAULT_DIRECTORY);
        String url = prefs.getString("url", DEFAULT_URL);
        api = new ClosedCodeApi(url);

        bindViews();
        bindActions();
        serverUrlInput.setText(url);
        directoryInput.setText(directory);
        workspacePath.setText(shortPath(directory));
        chatWorkspace.setText(shortPath(directory));
        serverSubtitle.setText(url);
        connectionUrl.setText(url);
        showPage("sessions");
        refreshEverything();
    }

    private void bindViews() {
        sessionsPage = findViewById(R.id.sessionsPage);
        connectionsPage = findViewById(R.id.connectionsPage);
        settingsPage = findViewById(R.id.settingsPage);
        chatPage = findViewById(R.id.chatPage);
        bottomNav = findViewById(R.id.bottomNav);
        sessionList = findViewById(R.id.sessionList);
        messageList = findViewById(R.id.messageList);
        messageScroll = findViewById(R.id.messageScroll);

        navSessions = findViewById(R.id.navSessions);
        navConnections = findViewById(R.id.navConnections);
        navSettings = findViewById(R.id.navSettings);
        headerStatus = findViewById(R.id.headerStatus);
        serverDot = findViewById(R.id.serverDot);
        serverState = findViewById(R.id.serverState);
        serverSubtitle = findViewById(R.id.serverSubtitle);
        workspacePath = findViewById(R.id.workspacePath);
        connectionBadge = findViewById(R.id.connectionBadge);
        connectionUrl = findViewById(R.id.connectionUrl);
        connectionVersion = findViewById(R.id.connectionVersion);
        chatTitle = findViewById(R.id.chatTitle);
        chatWorkspace = findViewById(R.id.chatWorkspace);
        modelChip = findViewById(R.id.modelChip);
        toolStatus = findViewById(R.id.toolStatus);
        composer = findViewById(R.id.composer);
        serverUrlInput = findViewById(R.id.serverUrlInput);
        directoryInput = findViewById(R.id.directoryInput);
        biometricSwitch = findViewById(R.id.biometricSwitch);
        hidePreviewSwitch = findViewById(R.id.hidePreviewSwitch);
        permissionNotifySwitch = findViewById(R.id.permissionNotifySwitch);
        questionNotifySwitch = findViewById(R.id.questionNotifySwitch);
        completedNotifySwitch = findViewById(R.id.completedNotifySwitch);
        errorNotifySwitch = findViewById(R.id.errorNotifySwitch);
    }

    private void bindActions() {
        navSessions.setOnClickListener(v -> showPage("sessions"));
        navConnections.setOnClickListener(v -> showPage("connections"));
        navSettings.setOnClickListener(v -> showPage("settings"));
        findViewById(R.id.refreshSessions).setOnClickListener(v -> refreshEverything());
        findViewById(R.id.newSessionButton).setOnClickListener(v -> createSession());
        findViewById(R.id.backButton).setOnClickListener(v -> closeChat());
        findViewById(R.id.sendButton).setOnClickListener(v -> sendPrompt());
        findViewById(R.id.filesButton).setOnClickListener(v -> showFiles("."));
        findViewById(R.id.diffButton).setOnClickListener(v -> showDiff());
        findViewById(R.id.saveBackend).setOnClickListener(v -> saveBackend());
        findViewById(R.id.serverStrip).setOnClickListener(v -> showPage("connections"));
        bindToggle(R.id.biometricRow, biometricSwitch, "requireBiometrics", false, false);
        bindToggle(R.id.hidePreviewRow, hidePreviewSwitch, "hideAppPreview", false, true);
        bindToggle(R.id.permissionNotifyRow, permissionNotifySwitch, "notifyPermissions", true, false);
        bindToggle(R.id.questionNotifyRow, questionNotifySwitch, "notifyQuestions", true, false);
        bindToggle(R.id.completedNotifyRow, completedNotifySwitch, "notifyCompleted", true, false);
        bindToggle(R.id.errorNotifyRow, errorNotifySwitch, "notifyErrors", true, false);
        composer.setImeOptions(EditorInfo.IME_ACTION_SEND);
        composer.setOnEditorActionListener((v, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_SEND) { sendPrompt(); return true; }
            return false;
        });
    }

    private void bindToggle(int rowId, Switch toggle, String key, boolean fallback, boolean securePreview) {
        toggle.setChecked(prefs.getBoolean(key, fallback));
        if (securePreview) setSecurePreview(toggle.isChecked());
        toggle.setOnCheckedChangeListener((button, checked) -> {
            prefs.edit().putBoolean(key, checked).apply();
            if (securePreview) setSecurePreview(checked);
        });
        findViewById(rowId).setOnClickListener(v -> toggle.setChecked(!toggle.isChecked()));
    }

    private void setSecurePreview(boolean enabled) {
        if (enabled) getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
    }

    private void showPage(String page) {
        api.stopEvents();
        sessionsPage.setVisibility("sessions".equals(page) ? View.VISIBLE : View.GONE);
        connectionsPage.setVisibility("connections".equals(page) ? View.VISIBLE : View.GONE);
        settingsPage.setVisibility("settings".equals(page) ? View.VISIBLE : View.GONE);
        chatPage.setVisibility(View.GONE);
        bottomNav.setVisibility(View.VISIBLE);
        tintNav(page);
        if ("sessions".equals(page)) refreshSessions();
        if ("connections".equals(page)) refreshHealth();
    }

    private void tintNav(String selected) {
        int accent = getColor(R.color.cc_accent);
        int muted = getColor(R.color.cc_muted);
        navSessions.setTextColor("sessions".equals(selected) ? accent : muted);
        navConnections.setTextColor("connections".equals(selected) ? accent : muted);
        navSettings.setTextColor("settings".equals(selected) ? accent : muted);
        navSessions.setTypeface(null, "sessions".equals(selected) ? Typeface.BOLD : Typeface.NORMAL);
        navConnections.setTypeface(null, "connections".equals(selected) ? Typeface.BOLD : Typeface.NORMAL);
        navSettings.setTypeface(null, "settings".equals(selected) ? Typeface.BOLD : Typeface.NORMAL);
    }

    private void refreshEverything() {
        refreshHealth();
        refreshProviders();
        refreshSessions();
    }

    private void refreshHealth() {
        setConnectionUi(false, "Checking", "—");
        api.health(new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                serverHealthy = true;
                try {
                    JSONObject obj = new JSONObject(body);
                    lastVersion = obj.optString("version", "unknown");
                } catch (Exception ignored) {
                    lastVersion = "unknown";
                }
                setConnectionUi(true, "Active", lastVersion);
            }
            @Override public void failure(String message) {
                serverHealthy = false;
                setConnectionUi(false, "Offline", "—");
                headerStatus.setText("● offline");
            }
        });
    }

    private void setConnectionUi(boolean healthy, String status, String version) {
        int color = getColor(healthy ? R.color.cc_good : R.color.cc_muted);
        headerStatus.setText(healthy ? "● connected" : "● " + status.toLowerCase());
        headerStatus.setTextColor(color);
        serverDot.setTextColor(color);
        serverState.setText(status);
        serverState.setTextColor(color);
        connectionBadge.setText(status);
        connectionBadge.setTextColor(color);
        connectionVersion.setText("Version " + version);
    }

    private void refreshProviders() {
        api.listProviders(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    Object root = body.trim().startsWith("[") ? new JSONArray(body) : new JSONObject(body);
                    String label = findModelLabel(root);
                    if (!TextUtils.isEmpty(label)) lastModelLabel = label;
                } catch (Exception ignored) {
                    lastModelLabel = "backend default";
                }
                modelChip.setText("Model: " + lastModelLabel);
            }
            @Override public void failure(String message) {
                modelChip.setText("Model: backend default");
            }
        });
    }

    private String findModelLabel(Object node) throws Exception {
        if (node instanceof JSONObject) {
            JSONObject obj = (JSONObject) node;
            String provider = obj.optString("id", obj.optString("name", ""));
            Object models = obj.opt("models");
            if (models instanceof JSONObject) {
                Iterator<String> keys = ((JSONObject) models).keys();
                if (keys.hasNext()) {
                    String model = keys.next();
                    return (provider.isEmpty() ? "" : provider + " / ") + model;
                }
            }
            if (models instanceof JSONArray && ((JSONArray) models).length() > 0) {
                JSONObject first = ((JSONArray) models).optJSONObject(0);
                if (first != null) {
                    String model = first.optString("id", first.optString("name", ""));
                    if (!model.isEmpty()) return (provider.isEmpty() ? "" : provider + " / ") + model;
                }
            }
            Iterator<String> keys = obj.keys();
            while (keys.hasNext()) {
                Object child = obj.opt(keys.next());
                if (child instanceof JSONObject || child instanceof JSONArray) {
                    String found = findModelLabel(child);
                    if (!TextUtils.isEmpty(found)) return found;
                }
            }
        } else if (node instanceof JSONArray) {
            JSONArray arr = (JSONArray) node;
            for (int i = 0; i < arr.length(); i++) {
                Object child = arr.opt(i);
                if (child instanceof JSONObject || child instanceof JSONArray) {
                    String found = findModelLabel(child);
                    if (!TextUtils.isEmpty(found)) return found;
                }
            }
        }
        return "";
    }

    private void refreshSessions() {
        sessionList.removeAllViews();
        TextView loading = simpleText("Loading sessions…", 13, R.color.cc_muted);
        loading.setPadding(dp(4), dp(14), dp(4), dp(14));
        sessionList.addView(loading);
        api.listSessions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                sessionList.removeAllViews();
                try {
                    JSONArray sessions = new JSONArray(body);
                    if (sessions.length() == 0) {
                        addEmptySessionHint();
                        return;
                    }
                    for (int i = 0; i < sessions.length(); i++) {
                        JSONObject session = sessions.optJSONObject(i);
                        if (session != null) addSessionRow(session);
                    }
                } catch (Exception e) {
                    addErrorRow("Could not parse sessions", e.getMessage());
                }
            }
            @Override public void failure(String message) {
                sessionList.removeAllViews();
                addErrorRow("Backend unavailable", message);
            }
        });
    }

    private void addEmptySessionHint() {
        TextView v = simpleText("No sessions yet.\nTap + to start coding.", 15, R.color.cc_muted);
        v.setGravity(Gravity.CENTER);
        v.setPadding(dp(18), dp(38), dp(18), dp(38));
        sessionList.addView(v);
    }

    private void addErrorRow(String title, String detail) {
        TextView v = simpleText(title + "\n" + detail, 13, R.color.cc_bad);
        v.setBackgroundResource(R.drawable.bg_card);
        v.setPadding(dp(16), dp(14), dp(16), dp(14));
        sessionList.addView(v, matchWrapMargins(0, 6, 0, 6));
    }

    private void addSessionRow(JSONObject session) {
        final String id = session.optString("id", "");
        final String title = session.optString("title", id.isEmpty() ? "Untitled session" : id);
        String directoryValue = session.optString("directory", "");
        String subtitle = directoryValue.isEmpty() ? shortPath(directory) : shortPath(directoryValue);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.VERTICAL);
        row.setBackgroundResource(R.drawable.bg_card);
        row.setPadding(dp(16), dp(14), dp(16), dp(14));
        TextView titleView = simpleText(title, 16, R.color.cc_text);
        titleView.setTypeface(null, Typeface.BOLD);
        TextView sub = simpleText(subtitle, 12, R.color.cc_muted);
        sub.setPadding(0, dp(5), 0, 0);
        row.addView(titleView);
        row.addView(sub);
        if (!id.isEmpty()) row.setOnClickListener(v -> openSession(id, title));
        sessionList.addView(row, matchWrapMargins(0, 6, 0, 6));
    }

    private void createSession() {
        if (!serverHealthy) {
            toast("ClosedCode server is offline");
            refreshHealth();
            return;
        }
        toolStatus.setText("Creating session…");
        api.createSession(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject session = new JSONObject(body);
                    String id = session.optString("id", "");
                    String title = session.optString("title", "New session");
                    if (id.isEmpty()) throw new IllegalStateException("Server returned no session id");
                    openSession(id, title);
                } catch (Exception e) {
                    toast("Create failed: " + e.getMessage());
                }
            }
            @Override public void failure(String message) {
                toast("Create failed: " + message);
            }
        });
    }

    private void openSession(String id, String title) {
        currentSessionId = id;
        sessionsPage.setVisibility(View.GONE);
        connectionsPage.setVisibility(View.GONE);
        settingsPage.setVisibility(View.GONE);
        chatPage.setVisibility(View.VISIBLE);
        bottomNav.setVisibility(View.GONE);
        chatTitle.setText(title);
        chatWorkspace.setText(shortPath(directory));
        modelChip.setText("Model: " + lastModelLabel);
        toolStatus.setText("Syncing…");
        loadMessages();
        startEventStream();
        pollRequests();
        refreshPendingInteractions();
    }

    private void closeChat() {
        api.stopEvents();
        currentSessionId = null;
        showPage("sessions");
    }

    private void loadMessages() {
        if (currentSessionId == null) return;
        final String expectedId = currentSessionId;
        api.messages(expectedId, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                renderMessages(body);
                toolStatus.setText("Idle");
            }
            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Error");
                toast("Messages: " + message);
            }
        });
    }

    private void renderMessages(String body) {
        messageList.removeAllViews();
        try {
            JSONArray arr = new JSONArray(body);
            for (int i = 0; i < arr.length(); i++) {
                JSONObject item = arr.optJSONObject(i);
                if (item == null) continue;
                JSONObject info = item.optJSONObject("info");
                String role = info == null ? "" : info.optString("role", "");
                JSONArray parts = item.optJSONArray("parts");
                if (parts == null) continue;
                for (int j = 0; j < parts.length(); j++) {
                    JSONObject part = parts.optJSONObject(j);
                    if (part == null) continue;
                    String type = part.optString("type", "");
                    if ("text".equals(type)) {
                        String text = part.optString("text", "");
                        if (!text.trim().isEmpty()) addMessageBubble(role, text);
                    } else if ("tool".equals(type)) {
                        addToolBubble(part);
                    } else if ("reasoning".equals(type)) {
                        String text = part.optString("text", "");
                        if (!text.trim().isEmpty()) addActivityLine("Thinking", text);
                    } else if ("step-start".equals(type) || "step-finish".equals(type)) {
                        addActivityLine(type, "");
                    }
                }
            }
            messageScroll.post(() -> messageScroll.fullScroll(View.FOCUS_DOWN));
        } catch (Exception e) {
            addMessageBubble("system", "Unable to parse message stream:\n" + e.getMessage());
        }
    }

    private void addMessageBubble(String role, String text) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(14), dp(12), dp(14), dp(12));
        box.setBackgroundResource(R.drawable.bg_card);
        TextView tag = simpleText("user".equals(role) ? "YOU" : "CLOSEDCODE", 10, R.color.cc_muted);
        tag.setTypeface(null, Typeface.BOLD);
        TextView body = simpleText(text, 15, R.color.cc_text);
        body.setPadding(0, dp(6), 0, 0);
        body.setTextIsSelectable(true);
        box.addView(tag);
        box.addView(body);
        messageList.addView(box, matchWrapMargins("user".equals(role) ? 42 : 0, 5, "user".equals(role) ? 0 : 20, 5));
    }

    private void addToolBubble(JSONObject part) {
        String tool = part.optString("tool", part.optString("name", "tool"));
        JSONObject state = part.optJSONObject("state");
        String status = state == null ? "running" : state.optString("status", "running");
        String title = state == null ? "" : state.optString("title", "");
        String text = "⚙ " + tool + "  ·  " + status + (title.isEmpty() ? "" : "\n" + title);
        TextView v = simpleText(text, 12, R.color.cc_muted);
        v.setBackgroundResource(R.drawable.bg_card);
        v.setPadding(dp(12), dp(10), dp(12), dp(10));
        messageList.addView(v, matchWrapMargins(0, 4, 36, 4));
        toolStatus.setText(tool + " · " + status);
    }

    private void addActivityLine(String label, String detail) {
        String text = detail.isEmpty() ? label : label + " · " + trim(detail, 100);
        TextView v = simpleText(text, 11, R.color.cc_muted);
        v.setPadding(dp(8), dp(4), dp(8), dp(4));
        messageList.addView(v);
    }

    private void sendPrompt() {
        if (currentSessionId == null) return;
        String text = composer.getText().toString().trim();
        if (text.isEmpty()) return;
        composer.setText("");
        addMessageBubble("user", text);
        toolStatus.setText("Sending…");
        final String expectedId = currentSessionId;
        api.promptAsync(expectedId, directory, text, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Running…");
                loadMessages();
            }
            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Error");
                addMessageBubble("system", "Prompt failed: " + message);
            }
        });
    }

    private void startEventStream() {
        api.startEvents(directory, new ClosedCodeApi.EventListener() {
            @Override public void event(String data) {
                if (currentSessionId == null) return;
                if (data.contains(currentSessionId) || data.contains("message") || data.contains("session")) {
                    toolStatus.setText("Live");
                    loadMessages();
                    pollRequests();
                }
                if (data.contains("permission") || data.contains("question")) refreshPendingInteractions();
            }
            @Override public void closed(String reason) {
                if (currentSessionId != null) toolStatus.setText("Stream reconnect needed");
            }
        });
    }

    private void refreshPendingInteractions() {
        if (currentSessionId == null || interactionDialogOpen) return;
        api.listPermissions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONArray pending = new JSONArray(body);
                    for (int i = 0; i < pending.length(); i++) {
                        JSONObject request = pending.optJSONObject(i);
                        if (request != null && currentSessionId.equals(request.optString("sessionID"))) {
                            showPermissionRequest(request);
                            return;
                        }
                    }
                } catch (Exception ignored) {}
                loadPendingQuestions();
            }
            @Override public void failure(String message) { loadPendingQuestions(); }
        });
    }

    private void showPermissionRequest(JSONObject request) {
        if (interactionDialogOpen) return;
        interactionDialogOpen = true;
        final String requestId = request.optString("id", "");
        final String permission = request.optString("permission", "Permission");
        JSONArray patterns = request.optJSONArray("patterns");
        StringBuilder detail = new StringBuilder(permission);
        if (patterns != null) for (int i = 0; i < patterns.length(); i++) detail.append("\n").append(patterns.optString(i));
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Permission request")
                .setMessage(detail.toString())
                .setPositiveButton("Allow once", (d, w) -> replyPermission(requestId, "once"))
                .setNeutralButton("Always", (d, w) -> replyPermission(requestId, "always"))
                .setNegativeButton("Reject", (d, w) -> replyPermission(requestId, "reject"))
                .create();
        dialog.setOnDismissListener(d -> { interactionDialogOpen = false; refreshPendingInteractions(); });
        dialog.show();
    }

    private void replyPermission(String requestId, String reply) {
        api.replyPermission(requestId, directory, reply, null, new ClosedCodeApi.Callback() {
            @Override public void success(String body) { toolStatus.setText("Permission " + reply); loadMessages(); }
            @Override public void failure(String message) { toast("Permission: " + message); }
        });
    }

    private void loadPendingQuestions() {
        if (currentSessionId == null || interactionDialogOpen) return;
        api.listQuestions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONArray pending = new JSONArray(body);
                    for (int i = 0; i < pending.length(); i++) {
                        JSONObject request = pending.optJSONObject(i);
                        if (request != null && currentSessionId.equals(request.optString("sessionID"))) {
                            JSONArray questions = request.optJSONArray("questions");
                            if (questions != null && questions.length() > 0) {
                                askQuestion(request.optString("id", ""), questions, 0, new JSONArray());
                                return;
                            }
                        }
                    }
                } catch (Exception e) { toast("Questions: " + e.getMessage()); }
            }
            @Override public void failure(String message) { }
        });
    }

    private void askQuestion(String requestId, JSONArray questions, int index, JSONArray answers) {
        if (index >= questions.length()) {
            interactionDialogOpen = false;
            api.replyQuestion(requestId, directory, answers, new ClosedCodeApi.Callback() {
                @Override public void success(String body) { toolStatus.setText("Question answered"); loadMessages(); }
                @Override public void failure(String message) { toast("Question: " + message); }
            });
            return;
        }
        JSONObject question = questions.optJSONObject(index);
        if (question == null) { answers.put(new JSONArray()); askQuestion(requestId, questions, index + 1, answers); return; }
        interactionDialogOpen = true;
        String title = question.optString("header", "Question");
        String prompt = question.optString("question", question.optString("prompt", "Choose an answer"));
        JSONArray options = question.optJSONArray("options");
        if (options == null || options.length() == 0) {
            EditText input = new EditText(this);
            input.setHint("Answer");
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setTitle(title).setMessage(prompt).setView(input)
                    .setPositiveButton("Submit", (d, w) -> { JSONArray a = new JSONArray(); a.put(input.getText().toString()); answers.put(a); interactionDialogOpen = false; askQuestion(requestId, questions, index + 1, answers); })
                    .setNegativeButton("Reject", (d, w) -> rejectQuestion(requestId)).create();
            dialog.setOnCancelListener(d -> { interactionDialogOpen = false; });
            dialog.show();
            return;
        }
        String[] labels = new String[options.length()];
        for (int i = 0; i < options.length(); i++) {
            JSONObject option = options.optJSONObject(i);
            labels[i] = option == null ? options.optString(i) : option.optString("label", option.optString("value", "Option " + (i + 1)));
        }
        boolean multiple = question.optBoolean("multiple", false);
        if (multiple) {
            boolean[] selected = new boolean[labels.length];
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setTitle(title + "\n" + prompt)
                    .setMultiChoiceItems(labels, selected, (d, which, checked) -> selected[which] = checked)
                    .setPositiveButton("Submit", (d, w) -> { JSONArray a = new JSONArray(); for (int i = 0; i < labels.length; i++) if (selected[i]) a.put(labels[i]); answers.put(a); interactionDialogOpen = false; askQuestion(requestId, questions, index + 1, answers); })
                    .setNegativeButton("Reject", (d, w) -> rejectQuestion(requestId)).create();
            dialog.setOnCancelListener(d -> { interactionDialogOpen = false; });
            dialog.show();
        } else {
            AlertDialog dialog = new AlertDialog.Builder(this)
                    .setTitle(title + "\n" + prompt)
                    .setItems(labels, (d, which) -> { JSONArray a = new JSONArray(); a.put(labels[which]); answers.put(a); interactionDialogOpen = false; askQuestion(requestId, questions, index + 1, answers); })
                    .setNegativeButton("Reject", (d, w) -> rejectQuestion(requestId)).create();
            dialog.setOnCancelListener(d -> { interactionDialogOpen = false; });
            dialog.show();
        }
    }

    private void rejectQuestion(String requestId) {
        interactionDialogOpen = false;
        api.rejectQuestion(requestId, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) { toolStatus.setText("Question rejected"); loadMessages(); }
            @Override public void failure(String message) { toast("Question: " + message); }
        });
    }

    private void pollRequests() {
        if (currentSessionId == null || requestDialogOpen) return;
        final String expectedId = currentSessionId;
        api.listPermissions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId) || requestDialogOpen) return;
                try {
                    JSONArray arr = new JSONArray(body);
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject request = arr.optJSONObject(i);
                        if (request != null && expectedId.equals(request.optString("sessionID"))) {
                            showPermissionRequest(request);
                            return;
                        }
                    }
                } catch (Exception ignored) {}
                pollQuestions(expectedId);
            }
            @Override public void failure(String message) {
                if (expectedId.equals(currentSessionId)) pollQuestions(expectedId);
            }
        });
    }

    private void pollQuestions(String expectedId) {
        if (requestDialogOpen || !expectedId.equals(currentSessionId)) return;
        api.listQuestions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId) || requestDialogOpen) return;
                try {
                    JSONArray arr = new JSONArray(body);
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject request = arr.optJSONObject(i);
                        if (request != null && expectedId.equals(request.optString("sessionID"))) {
                            showQuestionRequest(request);
                            return;
                        }
                    }
                } catch (Exception ignored) {}
            }
            @Override public void failure(String message) {}
        });
    }

    private void showPermissionRequest(JSONObject request) {
        requestDialogOpen = true;
        String id = request.optString("id");
        String permission = request.optString("permission", "Permission request");
        JSONArray patterns = request.optJSONArray("patterns");
        StringBuilder message = new StringBuilder(permission);
        if (patterns != null) {
            for (int i = 0; i < patterns.length(); i++) message.append("\n").append(patterns.optString(i));
        }
        new AlertDialog.Builder(this)
                .setTitle("Permission request")
                .setMessage(message.toString())
                .setPositiveButton("Allow once", (dialog, which) -> replyPermission(id, "once"))
                .setNeutralButton("Always allow", (dialog, which) -> replyPermission(id, "always"))
                .setNegativeButton("Deny", (dialog, which) -> replyPermission(id, "reject"))
                .setOnCancelListener(dialog -> { requestDialogOpen = false; })
                .show();
    }

    private void replyPermission(String id, String reply) {
        api.replyPermission(id, directory, reply, null, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                requestDialogOpen = false;
                toolStatus.setText("Permission " + reply);
                pollRequests();
            }
            @Override public void failure(String message) {
                requestDialogOpen = false;
                toast("Permission: " + message);
            }
        });
    }

    private void showQuestionRequest(JSONObject request) {
        requestDialogOpen = true;
        String id = request.optString("id");
        JSONArray questions = request.optJSONArray("questions");
        LinearLayout form = new LinearLayout(this);
        form.setOrientation(LinearLayout.VERTICAL);
        form.setPadding(dp(20), dp(8), dp(20), 0);
        List<EditText> answers = new ArrayList<>();
        if (questions != null) {
            for (int i = 0; i < questions.length(); i++) {
                JSONObject question = questions.optJSONObject(i);
                if (question == null) continue;
                String title = question.optString("header", "Question");
                String prompt = question.optString("question", "");
                JSONArray options = question.optJSONArray("options");
                StringBuilder description = new StringBuilder(title);
                if (!prompt.isEmpty()) description.append("\n").append(prompt);
                if (options != null && options.length() > 0) {
                    description.append("\nOptions: ");
                    for (int j = 0; j < options.length(); j++) {
                        JSONObject option = options.optJSONObject(j);
                        if (j > 0) description.append(", ");
                        description.append(option == null ? options.optString(j) : option.optString("label"));
                    }
                }
                TextView label = simpleText(description.toString(), 13, R.color.cc_text);
                label.setPadding(0, dp(8), 0, dp(4));
                EditText input = new EditText(this);
                input.setHint(question.optBoolean("multiple", false) ? "Answer(s), comma separated" : "Answer");
                input.setTextColor(getColor(R.color.cc_text));
                input.setHintTextColor(getColor(R.color.cc_muted));
                form.addView(label);
                form.addView(input, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
                answers.add(input);
            }
        }
        ScrollView scroll = new ScrollView(this);
        scroll.addView(form);
        new AlertDialog.Builder(this)
                .setTitle("ClosedCode question")
                .setView(scroll)
                .setPositiveButton("Reply", (dialog, which) -> {
                    JSONArray payload = new JSONArray();
                    for (EditText answer : answers) {
                        JSONArray selected = new JSONArray();
                        String raw = answer.getText().toString().trim();
                        if (!raw.isEmpty()) {
                            for (String value : raw.split(",")) {
                                String clean = value.trim();
                                if (!clean.isEmpty()) selected.put(clean);
                            }
                        }
                        payload.put(selected);
                    }
                    replyQuestion(id, payload);
                })
                .setNegativeButton("Reject", (dialog, which) -> rejectQuestion(id))
                .setOnCancelListener(dialog -> { requestDialogOpen = false; })
                .show();
    }

    private void replyQuestion(String id, JSONArray answers) {
        api.replyQuestion(id, directory, answers, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                requestDialogOpen = false;
                toolStatus.setText("Question answered");
                pollRequests();
            }
            @Override public void failure(String message) {
                requestDialogOpen = false;
                toast("Question: " + message);
            }
        });
    }

    private void rejectQuestion(String id) {
        api.rejectQuestion(id, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                requestDialogOpen = false;
                toolStatus.setText("Question rejected");
                pollRequests();
            }
            @Override public void failure(String message) {
                requestDialogOpen = false;
                toast("Question: " + message);
            }
        });
    }

    private void showFiles(String path) {
        api.listFiles(directory, path, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONArray arr = new JSONArray(body);
                    List<JSONObject> nodes = new ArrayList<>();
                    List<String> labels = new ArrayList<>();
                    if (!".".equals(path) && !path.isEmpty()) {
                        JSONObject up = new JSONObject();
                        up.put("name", "…");
                        up.put("path", parentPath(path));
                        up.put("type", "directory");
                        nodes.add(up);
                        labels.add("↰  …");
                    }
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject node = arr.optJSONObject(i);
                        if (node == null || node.optBoolean("ignored", false)) continue;
                        nodes.add(node);
                        labels.add(("directory".equals(node.optString("type")) ? "▸  " : "   ") + node.optString("name", node.optString("path")));
                    }
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle("Files · " + path)
                            .setItems(labels.toArray(new String[0]), (dialog, which) -> {
                                JSONObject node = nodes.get(which);
                                String nodePath = node.optString("path", ".");
                                if ("directory".equals(node.optString("type"))) showFiles(nodePath);
                                else showFile(nodePath);
                            })
                            .setNegativeButton("Close", null)
                            .show();
                } catch (Exception e) {
                    toast("Files: " + e.getMessage());
                }
            }
            @Override public void failure(String message) { toast("Files: " + message); }
        });
    }

    private void showFile(String path) {
        api.readFile(directory, path, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject obj = new JSONObject(body);
                    String content = obj.optString("content", body);
                    TextView text = simpleText(content, 12, R.color.cc_text);
                    text.setTextIsSelectable(true);
                    text.setPadding(dp(16), dp(10), dp(16), dp(10));
                    ScrollView scroll = new ScrollView(MainActivity.this);
                    scroll.setBackgroundColor(getColor(R.color.cc_bg));
                    scroll.addView(text);
                    new AlertDialog.Builder(MainActivity.this).setTitle(path).setView(scroll).setPositiveButton("Done", null).show();
                } catch (Exception e) {
                    toast("Read: " + e.getMessage());
                }
            }
            @Override public void failure(String message) { toast("Read: " + message); }
        });
    }

    private void showDiff() {
        if (currentSessionId == null) return;
        api.diff(currentSessionId, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                String pretty = body;
                try { pretty = new JSONArray(body).toString(2); } catch (Exception ignored) {}
                TextView text = simpleText(pretty, 12, R.color.cc_text);
                text.setTextIsSelectable(true);
                text.setPadding(dp(16), dp(10), dp(16), dp(10));
                ScrollView scroll = new ScrollView(MainActivity.this);
                scroll.setBackgroundColor(getColor(R.color.cc_bg));
                scroll.addView(text);
                new AlertDialog.Builder(MainActivity.this).setTitle("Session diff").setView(scroll).setPositiveButton("Done", null).show();
            }
            @Override public void failure(String message) { toast("Diff: " + message); }
        });
    }

    private void saveBackend() {
        String url = serverUrlInput.getText().toString().trim();
        String dir = directoryInput.getText().toString().trim();
        if (url.isEmpty()) url = DEFAULT_URL;
        if (dir.isEmpty()) dir = DEFAULT_DIRECTORY;
        directory = dir;
        api.setBaseUrl(url);
        prefs.edit().putString("url", url).putString("directory", dir).apply();
        serverSubtitle.setText(url);
        connectionUrl.setText(url);
        workspacePath.setText(shortPath(dir));
        chatWorkspace.setText(shortPath(dir));
        toast("Backend saved");
        showPage("connections");
        refreshEverything();
    }

    private String parentPath(String path) {
        if (path == null || path.isEmpty() || ".".equals(path)) return ".";
        int slash = path.lastIndexOf('/');
        return slash <= 0 ? "." : path.substring(0, slash);
    }

    private String shortPath(String path) {
        if (path == null) return "";
        String home = "/data/data/com.termux/files/home";
        return path.startsWith(home) ? "~" + path.substring(home.length()) : path;
    }

    private String trim(String text, int max) {
        if (text == null) return "";
        String one = text.replace('\n', ' ').trim();
        return one.length() <= max ? one : one.substring(0, max) + "…";
    }

    private TextView simpleText(String text, int sp, int colorResource) {
        TextView v = new TextView(this);
        v.setText(text);
        v.setTextColor(getColor(colorResource));
        v.setTextSize(sp);
        v.setLineSpacing(0f, 1.08f);
        return v;
    }

    private LinearLayout.LayoutParams matchWrapMargins(int left, int top, int right, int bottom) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        p.setMargins(dp(left), dp(top), dp(right), dp(bottom));
        return p;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void toast(String value) {
        Toast.makeText(this, value, Toast.LENGTH_LONG).show();
    }

    @Override protected void onDestroy() {
        api.shutdown();
        super.onDestroy();
    }
}
