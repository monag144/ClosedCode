#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/com/monag/closedcode/mobile/MainActivity.java"
text = path.read_text()

def once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_GUARD_{label}={count}")
    text = text.replace(old, new, 1)

once(
    "import android.view.Gravity;\nimport android.view.View;\nimport android.view.ViewGroup;\n",
    "import android.view.Gravity;\nimport android.view.View;\nimport android.view.ViewGroup;\nimport android.view.WindowManager;\nimport android.view.inputmethod.EditorInfo;\n",
    "IMPORT_VIEW",
)
once(
    "import android.widget.ScrollView;\nimport android.widget.TextView;\nimport android.widget.Toast;\n",
    "import android.widget.ScrollView;\nimport android.widget.Switch;\nimport android.widget.TextView;\nimport android.widget.Toast;\n",
    "IMPORT_SWITCH",
)
once(
    "    private EditText serverUrlInput;\n    private EditText directoryInput;\n",
    "    private EditText serverUrlInput;\n    private EditText directoryInput;\n    private Switch biometricSwitch;\n    private Switch hidePreviewSwitch;\n    private Switch permissionNotifySwitch;\n    private Switch questionNotifySwitch;\n    private Switch completedNotifySwitch;\n    private Switch errorNotifySwitch;\n    private boolean interactionDialogOpen;\n",
    "FIELDS",
)
once(
    "        serverUrlInput = findViewById(R.id.serverUrlInput);\n        directoryInput = findViewById(R.id.directoryInput);\n",
    "        serverUrlInput = findViewById(R.id.serverUrlInput);\n        directoryInput = findViewById(R.id.directoryInput);\n        biometricSwitch = findViewById(R.id.biometricSwitch);\n        hidePreviewSwitch = findViewById(R.id.hidePreviewSwitch);\n        permissionNotifySwitch = findViewById(R.id.permissionNotifySwitch);\n        questionNotifySwitch = findViewById(R.id.questionNotifySwitch);\n        completedNotifySwitch = findViewById(R.id.completedNotifySwitch);\n        errorNotifySwitch = findViewById(R.id.errorNotifySwitch);\n",
    "BIND_VIEWS",
)
once(
    "        findViewById(R.id.saveBackend).setOnClickListener(v -> saveBackend());\n    }\n\n    private void showPage(String page) {",
    "        findViewById(R.id.saveBackend).setOnClickListener(v -> saveBackend());\n        findViewById(R.id.serverStrip).setOnClickListener(v -> showPage(\"connections\"));\n        bindToggle(R.id.biometricRow, biometricSwitch, \"requireBiometrics\", false, false);\n        bindToggle(R.id.hidePreviewRow, hidePreviewSwitch, \"hideAppPreview\", false, true);\n        bindToggle(R.id.permissionNotifyRow, permissionNotifySwitch, \"notifyPermissions\", true, false);\n        bindToggle(R.id.questionNotifyRow, questionNotifySwitch, \"notifyQuestions\", true, false);\n        bindToggle(R.id.completedNotifyRow, completedNotifySwitch, \"notifyCompleted\", true, false);\n        bindToggle(R.id.errorNotifyRow, errorNotifySwitch, \"notifyErrors\", true, false);\n        composer.setImeOptions(EditorInfo.IME_ACTION_SEND);\n        composer.setOnEditorActionListener((v, actionId, event) -> {\n            if (actionId == EditorInfo.IME_ACTION_SEND) { sendPrompt(); return true; }\n            return false;\n        });\n    }\n\n    private void bindToggle(int rowId, Switch toggle, String key, boolean fallback, boolean securePreview) {\n        toggle.setChecked(prefs.getBoolean(key, fallback));\n        if (securePreview) setSecurePreview(toggle.isChecked());\n        toggle.setOnCheckedChangeListener((button, checked) -> {\n            prefs.edit().putBoolean(key, checked).apply();\n            if (securePreview) setSecurePreview(checked);\n        });\n        findViewById(rowId).setOnClickListener(v -> toggle.setChecked(!toggle.isChecked()));\n    }\n\n    private void setSecurePreview(boolean enabled) {\n        if (enabled) getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);\n        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_SECURE);\n    }\n\n    private void showPage(String page) {",
    "BIND_ACTIONS",
)
once(
    "        loadMessages();\n        startEventStream();\n    }\n",
    "        loadMessages();\n        startEventStream();\n        refreshPendingInteractions();\n    }\n",
    "OPEN_SESSION",
)
once(
    "                if (data.contains(currentSessionId) || data.contains(\"message\") || data.contains(\"session\")) {\n                    toolStatus.setText(\"Live\");\n                    loadMessages();\n                }\n",
    "                if (data.contains(currentSessionId) || data.contains(\"message\") || data.contains(\"session\")) {\n                    toolStatus.setText(\"Live\");\n                    loadMessages();\n                }\n                if (data.contains(\"permission\") || data.contains(\"question\")) refreshPendingInteractions();\n",
    "EVENTS",
)
once(
    "    private void showFiles(String path) {",
    r'''    private void refreshPendingInteractions() {
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

    private void showFiles(String path) {''',
    "INTERACTIONS",
)

path.write_text(text)
print("MAINACTIVITY_PATCH=GREEN")
