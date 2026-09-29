#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/com/monag/closedcode/mobile/MainActivity.java"
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_GUARD_{label}={count}")
    text = text.replace(old, new, 1)

if "private boolean requestDialogOpen;" not in text:
    replace_once(
        '    private String lastModelLabel = "backend default";\n',
        '    private String lastModelLabel = "backend default";\n    private boolean requestDialogOpen;\n',
        "FIELD",
    )

if "pollRequests();" not in text:
    replace_once(
        '        loadMessages();\n        startEventStream();\n',
        '        loadMessages();\n        startEventStream();\n        pollRequests();\n',
        "OPEN_SESSION",
    )

if "private void pollRequests()" not in text:
    marker = '    private void showFiles(String path) {\n'
    methods = r'''    private void pollRequests() {
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

'''
    replace_once(marker, methods + marker, "METHODS")

# Ensure live events also surface newly-created permission/question requests.
event_old = '                    toolStatus.setText("Live");\n                    loadMessages();\n'
event_new = '                    toolStatus.setText("Live");\n                    loadMessages();\n                    pollRequests();\n'
if event_new not in text:
    replace_once(event_old, event_new, "EVENT_POLL")

path.write_text(text)
print("MOBILE_V011_LOGIC_PATCH=GREEN")
