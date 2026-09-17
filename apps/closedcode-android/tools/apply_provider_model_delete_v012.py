from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src/com/monag/closedcode/mobile/MainActivity.java"
API = ROOT / "src/com/monag/closedcode/mobile/ClosedCodeApi.java"
BUILD = ROOT / "build-termux.sh"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_GUARD_{label}={count}")
    return text.replace(old, new, 1)


def replace_between(text: str, start: str, end: str, body: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"PATCH_BOUNDARY_{label}_START={text.count(start)}_END={text.count(end)}")
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + body + text[b:]

# --- ClosedCodeApi ---------------------------------------------------------
a = API.read_text()
a = replace_once(
    a,
    '''    public void createSession(String directory, Callback cb) {\n        async("POST", "/session?" + routing(directory), null, cb);\n    }\n\n''',
    '''    public void createSession(String directory, Callback cb) {\n        async("POST", "/session?" + routing(directory), null, cb);\n    }\n\n    public void deleteSession(String sessionId, String directory, Callback cb) {\n        async("DELETE", "/session/" + enc(sessionId) + "?" + routing(directory), null, cb);\n    }\n\n''',
    "API_DELETE_SESSION",
)

prompt_start = '    public void promptAsync(String sessionId, String directory, String text, Callback cb) {'
prompt_end = '    public void abort(String sessionId, String directory, Callback cb) {'
prompt_body = '''    public void promptAsync(String sessionId, String directory, String text, Callback cb) {\n        promptAsync(sessionId, directory, text, null, null, cb);\n    }\n\n    public void promptAsync(String sessionId, String directory, String text, String providerId, String modelId, Callback cb) {\n        try {\n            JSONObject body = new JSONObject();\n            JSONArray parts = new JSONArray();\n            JSONObject part = new JSONObject();\n            part.put("type", "text");\n            part.put("text", text);\n            parts.put(part);\n            body.put("parts", parts);\n            if (providerId != null && !providerId.trim().isEmpty() && modelId != null && !modelId.trim().isEmpty()) {\n                JSONObject model = new JSONObject();\n                model.put("providerID", providerId);\n                model.put("modelID", modelId);\n                body.put("model", model);\n            }\n            async("POST", "/session/" + enc(sessionId) + "/prompt_async?" + routing(directory), body.toString(), cb);\n        } catch (Exception e) {\n            main.post(() -> cb.failure(e.toString()));\n        }\n    }\n\n'''
a = replace_between(a, prompt_start, prompt_end, prompt_body, "API_PROMPT_MODEL")
API.write_text(a)

# --- MainActivity ----------------------------------------------------------
t = MAIN.read_text()
t = replace_once(
    t,
    '    private String lastModelLabel = "backend default";\n',
    '''    private String lastModelLabel = "backend default";\n    private String selectedProviderId;\n    private String selectedModelId;\n    private final List<ProviderChoice> providerChoices = new ArrayList<>();\n\n    private static final class ModelChoice {\n        final String id;\n        final String name;\n\n        ModelChoice(String id, String name) {\n            this.id = id;\n            this.name = name;\n        }\n    }\n\n    private static final class ProviderChoice {\n        final String id;\n        final String name;\n        final boolean connected;\n        final List<ModelChoice> models = new ArrayList<>();\n\n        ProviderChoice(String id, String name, boolean connected) {\n            this.id = id;\n            this.name = name;\n            this.connected = connected;\n        }\n    }\n''',
    "MAIN_PROVIDER_FIELDS",
)

t = replace_once(
    t,
    '        findViewById(R.id.serverStrip).setOnClickListener(v -> showPage("connections"));\n',
    '        findViewById(R.id.serverStrip).setOnClickListener(v -> showPage("connections"));\n        modelChip.setOnClickListener(v -> showProviderPicker());\n',
    "MAIN_MODEL_CLICK",
)

refresh_start = '    private void refreshProviders() {'
refresh_end = '    private void refreshSessions() {'
refresh_body = r'''    private void refreshProviders() {
        api.listProviders(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject root = new JSONObject(body);
                    parseProviderCatalog(root);
                } catch (Exception e) {
                    providerChoices.clear();
                    selectedProviderId = null;
                    selectedModelId = null;
                    lastModelLabel = "backend default";
                }
                modelChip.setText("Model: " + lastModelLabel);
            }
            @Override public void failure(String message) {
                providerChoices.clear();
                modelChip.setText("Model: " + lastModelLabel);
            }
        });
    }

    private void parseProviderCatalog(JSONObject root) {
        providerChoices.clear();
        java.util.HashSet<String> connected = new java.util.HashSet<>();
        JSONArray connectedArray = root.optJSONArray("connected");
        if (connectedArray != null) {
            for (int i = 0; i < connectedArray.length(); i++) connected.add(connectedArray.optString(i));
        }

        List<ProviderChoice> preferred = new ArrayList<>();
        List<ProviderChoice> others = new ArrayList<>();
        JSONArray all = root.optJSONArray("all");
        if (all != null) {
            for (int i = 0; i < all.length(); i++) {
                JSONObject provider = all.optJSONObject(i);
                if (provider == null) continue;
                String providerId = provider.optString("id", "");
                if (providerId.isEmpty()) continue;
                ProviderChoice choice = new ProviderChoice(
                        providerId,
                        provider.optString("name", providerId),
                        connected.contains(providerId));
                JSONObject models = provider.optJSONObject("models");
                if (models != null) {
                    List<ModelChoice> starred = new ArrayList<>();
                    List<ModelChoice> regular = new ArrayList<>();
                    Iterator<String> keys = models.keys();
                    while (keys.hasNext()) {
                        String key = keys.next();
                        JSONObject model = models.optJSONObject(key);
                        String modelId = model == null ? key : model.optString("id", key);
                        String modelName = model == null ? modelId : model.optString("name", modelId);
                        ModelChoice item = new ModelChoice(modelId, modelName);
                        if (isGlmFlash(modelId, modelName) || isNeo(modelId, modelName)) starred.add(item);
                        else regular.add(item);
                    }
                    choice.models.addAll(starred);
                    choice.models.addAll(regular);
                }
                if (hasPreferredModel(choice)) preferred.add(choice); else others.add(choice);
            }
        }
        providerChoices.addAll(preferred);
        providerChoices.addAll(others);

        String savedProvider = prefs.getString("selectedProviderId", null);
        String savedModel = prefs.getString("selectedModelId", null);
        ProviderChoice savedP = findProvider(savedProvider);
        ModelChoice savedM = findModel(savedP, savedModel);
        if (savedP != null && savedM != null && savedP.connected) {
            applyModelChoice(savedP, savedM, false);
            return;
        }

        for (ProviderChoice provider : providerChoices) {
            if (!provider.connected) continue;
            for (ModelChoice model : provider.models) {
                if (isGlmFlash(model.id, model.name)) {
                    applyModelChoice(provider, model, true);
                    return;
                }
            }
        }
        selectedProviderId = null;
        selectedModelId = null;
        lastModelLabel = "backend default";
    }

    private void showProviderPicker() {
        if (providerChoices.isEmpty()) {
            toast("Provider catalog is still loading");
            refreshProviders();
            return;
        }
        String[] labels = new String[providerChoices.size()];
        for (int i = 0; i < providerChoices.size(); i++) {
            ProviderChoice provider = providerChoices.get(i);
            String stars = hasGlmFlash(provider) ? "★ GLM  " : hasNeo(provider) ? "★ Neo  " : "";
            labels[i] = stars + provider.name + (provider.connected ? "  · connected" : "  · not connected");
        }
        new AlertDialog.Builder(this)
                .setTitle("Choose provider")
                .setItems(labels, (dialog, which) -> showModelPicker(providerChoices.get(which)))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showModelPicker(ProviderChoice provider) {
        if (provider.models.isEmpty()) {
            toast("No models reported for " + provider.name);
            return;
        }
        String[] labels = new String[provider.models.size()];
        for (int i = 0; i < provider.models.size(); i++) {
            ModelChoice model = provider.models.get(i);
            String star = isGlmFlash(model.id, model.name) ? "★ GLM-4.7-Flash  " : isNeo(model.id, model.name) ? "★ Neo  " : "";
            labels[i] = star + model.name + (model.name.equals(model.id) ? "" : "\n" + model.id);
        }
        new AlertDialog.Builder(this)
                .setTitle(provider.name + (provider.connected ? "" : " · not connected"))
                .setItems(labels, (dialog, which) -> {
                    if (!provider.connected) {
                        toast("Connect " + provider.name + " in the ClosedCode backend first");
                        return;
                    }
                    applyModelChoice(provider, provider.models.get(which), true);
                })
                .setNegativeButton("Back", (dialog, which) -> showProviderPicker())
                .show();
    }

    private void applyModelChoice(ProviderChoice provider, ModelChoice model, boolean persist) {
        selectedProviderId = provider.id;
        selectedModelId = model.id;
        lastModelLabel = provider.name + " / " + model.name;
        modelChip.setText("Model: " + lastModelLabel);
        if (persist) {
            prefs.edit()
                    .putString("selectedProviderId", selectedProviderId)
                    .putString("selectedModelId", selectedModelId)
                    .apply();
        }
    }

    private ProviderChoice findProvider(String id) {
        if (id == null) return null;
        for (ProviderChoice provider : providerChoices) if (id.equals(provider.id)) return provider;
        return null;
    }

    private ModelChoice findModel(ProviderChoice provider, String id) {
        if (provider == null || id == null) return null;
        for (ModelChoice model : provider.models) if (id.equals(model.id)) return model;
        return null;
    }

    private boolean hasPreferredModel(ProviderChoice provider) {
        return hasGlmFlash(provider) || hasNeo(provider);
    }

    private boolean hasGlmFlash(ProviderChoice provider) {
        for (ModelChoice model : provider.models) if (isGlmFlash(model.id, model.name)) return true;
        return false;
    }

    private boolean hasNeo(ProviderChoice provider) {
        for (ModelChoice model : provider.models) if (isNeo(model.id, model.name)) return true;
        return false;
    }

    private static boolean isGlmFlash(String id, String name) {
        String value = ((id == null ? "" : id) + " " + (name == null ? "" : name)).toLowerCase();
        return value.contains("glm-4.7-flash") || value.contains("glm 4.7 flash");
    }

    private static boolean isNeo(String id, String name) {
        String value = ((id == null ? "" : id) + " " + (name == null ? "" : name)).toLowerCase();
        return value.contains("nemotron");
    }

'''
t = replace_between(t, refresh_start, refresh_end, refresh_body, "MAIN_PROVIDER_CATALOG")

session_start = '    private void addSessionRow(JSONObject session) {'
session_end = '    private void createSession() {'
session_body = r'''    private void addSessionRow(JSONObject session) {
        final String id = session.optString("id", "");
        final String title = session.optString("title", id.isEmpty() ? "Untitled session" : id);
        String directoryValue = session.optString("directory", "");
        String subtitle = directoryValue.isEmpty() ? shortPath(directory) : shortPath(directoryValue);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.VERTICAL);
        row.setBackgroundResource(R.drawable.bg_card);
        row.setPadding(dp(16), dp(14), dp(16), dp(12));
        TextView titleView = simpleText(title, 16, R.color.cc_text);
        titleView.setTypeface(null, Typeface.BOLD);
        TextView sub = simpleText(subtitle, 12, R.color.cc_muted);
        sub.setPadding(0, dp(5), 0, 0);
        row.addView(titleView);
        row.addView(sub);
        if (!id.isEmpty()) {
            TextView delete = simpleText("Delete session", 12, R.color.cc_bad);
            delete.setGravity(Gravity.END);
            delete.setPadding(dp(8), dp(10), 0, dp(2));
            delete.setOnClickListener(v -> confirmDeleteSession(id, title));
            row.addView(delete);
            row.setOnClickListener(v -> openSession(id, title));
        }
        sessionList.addView(row, matchWrapMargins(0, 6, 0, 6));
    }

    private void confirmDeleteSession(String id, String title) {
        new AlertDialog.Builder(this)
                .setTitle("Delete session?")
                .setMessage(title + "\n\nThis permanently removes the session and its message history.")
                .setPositiveButton("Delete", (dialog, which) -> deleteSession(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteSession(String id) {
        api.deleteSession(id, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (id.equals(currentSessionId)) closeChat();
                else refreshSessions();
                toast("Session deleted");
            }
            @Override public void failure(String message) {
                toast("Delete failed: " + message);
            }
        });
    }

'''
t = replace_between(t, session_start, session_end, session_body, "MAIN_DELETE_SESSION")

send_start = '    private void sendPrompt() {'
send_end = '    private void startEventStream() {'
send_body = r'''    private void sendPrompt() {
        if (currentSessionId == null) return;
        String text = composer.getText().toString().trim();
        if (text.isEmpty()) return;
        composer.setText("");
        addMessageBubble("user", text);
        toolStatus.setText("Sending…");
        final String expectedId = currentSessionId;
        api.promptAsync(expectedId, directory, text, selectedProviderId, selectedModelId, new ClosedCodeApi.Callback() {
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

'''
t = replace_between(t, send_start, send_end, send_body, "MAIN_PROMPT_MODEL")

MAIN.write_text(t)

# --- build version --------------------------------------------------------
b = BUILD.read_text()
b = replace_once(b, 'OUT_NAME="ClosedCode-cleanroom-v0.1.1-debug.apk"', 'OUT_NAME="ClosedCode-cleanroom-v0.1.2-debug.apk"', 'BUILD_OUT')
b = replace_once(b, '--version-code 3 \\\n  --version-name "0.1.1-cleanroom" \\\n', '--version-code 4 \\\n  --version-name "0.1.2-cleanroom" \\\n', 'BUILD_VERSION')
b = replace_once(b, 'echo "VERSION_NAME=0.1.1-cleanroom"', 'echo "VERSION_NAME=0.1.2-cleanroom"', 'BUILD_VERSION_ECHO')
BUILD.write_text(b)

print("PROVIDER_MODEL_DELETE_V012_PATCH=GREEN")
