package com.monag.closedcode.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.content.Intent;
import android.speech.RecognizerIntent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.animation.PathInterpolator;
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
    private TextView agentChip;
    private TextView effortChip;
    private TextView voiceButton;
    private TextView toolStatus;
    private TextView copySessionButton;
    private TextView sendButton;
    private TextView stopButton;
    private ContextUsageView usageButton;
    private EditText composer;
    private EditText serverUrlInput;
    private EditText directoryInput;
    private Switch biometricSwitch;
    private Switch hidePreviewSwitch;
    private Switch yoloSwitch;
    private Switch fullAccessSwitch;
    private Switch permissionNotifySwitch;
    private Switch questionNotifySwitch;
    private Switch completedNotifySwitch;
    private Switch errorNotifySwitch;
    private TextView completionSoundToggle;
    private TextView completionSoundChoose;
    private TextView completionSoundTest;
    private TextView completionSoundLabel;
    private TextView themeValue;
    private boolean interactionDialogOpen;
    private boolean pageTransitionRunning;
    private boolean promptRunning;
    private int streamGeneration;
    private int eventReconnectAttempt;
    private boolean passthroughSendActive;
    private boolean appVisible;
    private boolean providerRunHadError;
    private String lastCompletionAlertRequestId;
    private String lastErrorAlertRequestId;
    private static final String COMPLETION_CHANNEL_ID = "closedcode_agent_completion";
    private static final String ERROR_CHANNEL_ID = "closedcode_agent_error";
    private static final long PAGE_TRANSITION_MS = 240L;
    private static final PathInterpolator PAGE_TRANSITION_INTERPOLATOR =
            new PathInterpolator(0.22f, 1f, 0.36f, 1f);

    private SharedPreferences prefs;
    private ClosedCodeApi api;
    private ComposerUiController composerUi;
    private String directory;
    private String currentSessionId;
    private boolean serverHealthy;
    private String lastVersion = "—";
    private String lastModelLabel = "backend default";
    private String selectedProviderId;
    private String selectedModelId;
    private String selectedAgent = "build";
    private String selectedVariant;
    private String activeProviderRequestId;
    private AlertDialog activeAgentPermissionDialog;
    private String pendingAgentPermissionExpectedId;
    private String pendingAgentPermissionRequestId;
    private String pendingAgentPermissionId;
    private String pendingAgentPermissionTool;
    private String pendingAgentPermissionArguments;
    private final java.util.HashSet<String> approveAllAgentRequests = new java.util.HashSet<>();
    private TextView providerStreamBody;
    private final StringBuilder providerStreamText = new StringBuilder();
    private final List<View> selectedTranscriptBlocks = new ArrayList<>();
    private boolean transcriptSelectionMode;
    private static final int VOICE_REQUEST_CODE = 413;
    private static final int SOUND_REQUEST_CODE = 414;
    private final List<ProviderChoice> providerChoices = new ArrayList<>();

    private static final class ModelChoice {
        final String id;
        final String name;

        ModelChoice(String id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    private static final class ProviderChoice {
        final String id;
        final String name;
        final boolean connected;
        final List<ModelChoice> models = new ArrayList<>();

        ProviderChoice(String id, String name, boolean connected) {
            this.id = id;
            this.name = name;
            this.connected = connected;
        }
    }

    @Override
    protected void onCreate(Bundle state) {
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        applySavedTheme();
        super.onCreate(state);
        setContentView(R.layout.activity_main);
        directory = prefs.getString("directory", DEFAULT_DIRECTORY);
        String url = prefs.getString("url", DEFAULT_URL);
        api = new ClosedCodeApi(url);

        bindViews();
        composerUi = new ComposerUiController(
                this,
                api,
                prefs,
                modelChip,
                agentChip,
                effortChip,
                usageButton,
                directory);
        bindActions();
        serverUrlInput.setText(url);
        directoryInput.setText(directory);
        workspacePath.setText(shortPath(directory));
        chatWorkspace.setText(shortPath(directory));
        serverSubtitle.setText(url);
        connectionUrl.setText(url);
        ensureCompletionChannel();
        requestCompletionPermission();
        updateCompletionSoundUi();
        showPage("sessions");
        handleCompletionIntent(getIntent());
        refreshEverything();
    }

    private void applySavedTheme() {
        String value=prefs.getString("appTheme","dark");
        if("light".equals(value)) setTheme(R.style.Theme_ClosedCode_Light);
        else if("chocolate_mint".equals(value)) setTheme(R.style.Theme_ClosedCode_ChocolateMint);
        else setTheme(R.style.Theme_ClosedCode);
    }

    private void updateThemeUi() {
        if(themeValue==null)return; String value=prefs.getString("appTheme","dark");
        themeValue.setText("light".equals(value)?"Light":"chocolate_mint".equals(value)?"Chocolate Mint":"Dark");
    }

    private void applyThemeSpecificControls() {
        if (!"chocolate_mint".equals(prefs.getString("appTheme", "dark"))) return;
        android.content.res.ColorStateList mint = android.content.res.ColorStateList.valueOf(getColor(R.color.cc_mint_accent));
        int black = android.graphics.Color.rgb(16, 16, 16);
        TextView[] controls = {modelChip, agentChip, effortChip, voiceButton, stopButton};
        for (TextView control : controls) {
            if (control == null) continue;
            control.setBackgroundTintList(mint);
            control.setTextColor(black);
        }
    }

    private void showThemePicker() {
        String[] labels={"Dark","Light","Chocolate Mint"}; String[] values={"dark","light","chocolate_mint"}; String current=prefs.getString("appTheme","dark"); int checked=0;
        for(int i=0;i<values.length;i++) if(values[i].equals(current)) checked=i;
        new AlertDialog.Builder(this).setTitle("Theme").setSingleChoiceItems(labels,checked,(d,which)->{ prefs.edit().putString("appTheme",values[which]).apply(); d.dismiss(); recreate(); }).setNegativeButton("Cancel",null).show();
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
        agentChip = findViewById(R.id.agentChip);
        effortChip = findViewById(R.id.effortChip);
        voiceButton = findViewById(R.id.voiceButton);
        toolStatus = findViewById(R.id.toolStatus);
        copySessionButton = findViewById(R.id.copySessionButton);
        sendButton = findViewById(R.id.sendButton);
        stopButton = findViewById(R.id.stopButton);
        usageButton = findViewById(R.id.usageButton);
        composer = findViewById(R.id.composer);
        serverUrlInput = findViewById(R.id.serverUrlInput);
        directoryInput = findViewById(R.id.directoryInput);
        biometricSwitch = findViewById(R.id.biometricSwitch);
        hidePreviewSwitch = findViewById(R.id.hidePreviewSwitch);
        yoloSwitch = findViewById(R.id.yoloSwitch);
        fullAccessSwitch = findViewById(R.id.fullAccessSwitch);
        permissionNotifySwitch = findViewById(R.id.permissionNotifySwitch);
        questionNotifySwitch = findViewById(R.id.questionNotifySwitch);
        completedNotifySwitch = findViewById(R.id.completedNotifySwitch);
        errorNotifySwitch = findViewById(R.id.errorNotifySwitch);
        completionSoundToggle = findViewById(R.id.completionSoundToggle);
        completionSoundChoose = findViewById(R.id.completionSoundChoose);
        completionSoundTest = findViewById(R.id.completionSoundTest);
        completionSoundLabel = findViewById(R.id.completionSoundLabel);
        themeValue = findViewById(R.id.themeValue);
    }

    private void bindActions() {
        navSessions.setOnClickListener(v -> showPage("sessions"));
        navConnections.setOnClickListener(v -> showPage("connections"));
        navSettings.setOnClickListener(v -> showPage("settings"));
        findViewById(R.id.refreshSessions).setOnClickListener(v -> refreshEverything());
        findViewById(R.id.newSessionButton).setOnClickListener(v -> createSession());
        findViewById(R.id.backButton).setOnClickListener(v -> closeChat());
        copySessionButton.setOnClickListener(v -> copySessionTranscript());
        sendButton.setOnClickListener(v -> sendPrompt());
        stopButton.setOnClickListener(v -> abortPrompt());
        findViewById(R.id.filesButton).setOnClickListener(v -> showFiles("."));
        findViewById(R.id.diffButton).setOnClickListener(v -> showDiff());
        findViewById(R.id.runButton).setOnClickListener(v -> showRunCommand());
        findViewById(R.id.saveBackend).setOnClickListener(v -> saveBackend());
        findViewById(R.id.serverStrip).setOnClickListener(v -> showPage("connections"));
        modelChip.setOnClickListener(v -> composerUi.showModelPicker());
        agentChip.setOnClickListener(v -> composerUi.showAgentPicker());
        effortChip.setOnClickListener(v -> composerUi.showEffortPicker());
        usageButton.setOnClickListener(v -> composerUi.showUsage());
        voiceButton.setOnClickListener(v -> startVoiceInput());
        findViewById(R.id.themeRow).setOnClickListener(v -> showThemePicker());
        updateThemeUi();
        applyThemeSpecificControls();
        bindToggle(R.id.biometricRow, biometricSwitch, "requireBiometrics", false, false);
        bindToggle(R.id.hidePreviewRow, hidePreviewSwitch, "hideAppPreview", false, true);
        bindAutonomyControls();
        bindToggle(R.id.permissionNotifyRow, permissionNotifySwitch, "notifyPermissions", true, false);
        bindToggle(R.id.questionNotifyRow, questionNotifySwitch, "notifyQuestions", true, false);
        bindToggle(R.id.completedNotifyRow, completedNotifySwitch, "notifyCompleted", true, false);
        bindToggle(R.id.errorNotifyRow, errorNotifySwitch, "notifyErrors", true, false);
        completionSoundToggle.setOnClickListener(v -> {
            boolean enabled = !prefs.getBoolean("completionSoundEnabled", true);
            prefs.edit().putBoolean("completionSoundEnabled", enabled).apply();
            updateCompletionSoundUi();
            if (enabled) playCompletionSound(true);
        });
        completionSoundChoose.setOnClickListener(v -> chooseCompletionSound());
        completionSoundTest.setOnClickListener(v -> playCompletionSound(true));
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
            if (("notifyCompleted".equals(key) || "notifyErrors".equals(key)) && checked) requestCompletionPermission();
        });
        findViewById(rowId).setOnClickListener(v -> toggle.setChecked(!toggle.isChecked()));
    }

    private void syncAutonomy() { boolean f=prefs.getBoolean("fullAccessAutonomy",false); if(f&&prefs.getBoolean("yoloAutonomy",false)) prefs.edit().putBoolean("yoloAutonomy",false).apply(); yoloSwitch.setChecked(!f&&prefs.getBoolean("yoloAutonomy",false)); fullAccessSwitch.setChecked(f); }
    private void bindAutonomyControls() { syncAutonomy(); findViewById(R.id.yoloRow).setOnClickListener(v->{ boolean on=!prefs.getBoolean("yoloAutonomy",false); android.content.SharedPreferences.Editor e=prefs.edit().putBoolean("yoloAutonomy",on); if(on)e.putBoolean("fullAccessAutonomy",false); e.apply(); syncAutonomy(); }); findViewById(R.id.fullAccessRow).setOnClickListener(v->{ if(prefs.getBoolean("fullAccessAutonomy",false)){prefs.edit().putBoolean("fullAccessAutonomy",false).apply();syncAutonomy();return;} new AlertDialog.Builder(this).setTitle("Enable Full Access?").setMessage("DANGER: removes ClosedCode's workspace boundary. The agent may read, write, delete, move, and run shell commands anywhere Termux is allowed by Android/Linux. No tool approval prompts are shown. OS permissions still apply.").setPositiveButton("Enable Full Access",(d,w)->{prefs.edit().putBoolean("fullAccessAutonomy",true).putBoolean("yoloAutonomy",false).apply();syncAutonomy();}).setNegativeButton("Cancel",null).show(); }); }

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
        composerUi.refresh(directory);
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

    private void showAgentPicker() {
        final String[] labels = {"Build", "Plan"};
        int selected = "plan".equals(selectedAgent) ? 1 : 0;
        new AlertDialog.Builder(this)
                .setTitle("Agent mode")
                .setSingleChoiceItems(labels, selected, (dialog, which) -> {
                    selectedAgent = which == 1 ? "plan" : "build";
                    prefs.edit().putString("selectedAgent", selectedAgent).apply();
                    updateComposerControlLabels();
                    dialog.dismiss();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showEffortPicker() {
        final String[] labels = {"Auto", "Low", "Medium", "High"};
        String current = selectedVariant == null ? "auto" : selectedVariant;
        int selected = "low".equals(current) ? 1 : "medium".equals(current) ? 2 : "high".equals(current) ? 3 : 0;
        new AlertDialog.Builder(this)
                .setTitle("Reasoning effort")
                .setSingleChoiceItems(labels, selected, (dialog, which) -> {
                    String value = which == 1 ? "low" : which == 2 ? "medium" : which == 3 ? "high" : "auto";
                    selectedVariant = "auto".equals(value) ? null : value;
                    prefs.edit().putString("selectedVariant", value).apply();
                    updateComposerControlLabels();
                    dialog.dismiss();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void updateComposerControlLabels() {
        if (agentChip != null) agentChip.setText("plan".equals(selectedAgent) ? "Plan" : "Build");
        if (effortChip != null) {
            String value = selectedVariant == null ? "Auto" : selectedVariant.substring(0, 1).toUpperCase() + selectedVariant.substring(1);
            effortChip.setText("Reason: " + value);
        }
    }

    private void startVoiceInput() {
        try {
            Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak to ClosedCode");
            startActivityForResult(intent, VOICE_REQUEST_CODE);
        } catch (Exception e) {
            toast("Voice input unavailable: " + e.getMessage());
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SOUND_REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                android.net.Uri picked = data.getParcelableExtra(android.media.RingtoneManager.EXTRA_RINGTONE_PICKED_URI);
                if (picked != null) {
                    prefs.edit().putString("completionSoundUri", picked.toString()).apply();
                    updateCompletionSoundUi();
                    playCompletionSound(true);
                }
            }
            return;
        }
        if (requestCode != VOICE_REQUEST_CODE || resultCode != RESULT_OK || data == null) return;
        ArrayList<String> results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
        if (results == null || results.isEmpty()) return;
        String spoken = results.get(0).trim();
        if (spoken.isEmpty()) return;
        String existing = composer.getText().toString();
        composer.setText(existing.isEmpty() ? spoken : existing + " " + spoken);
        composer.setSelection(composer.length());
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
        row.setPadding(dp(16), dp(14), dp(16), dp(12));
        TextView titleView = simpleText(title, 16, R.color.cc_text);
        titleView.setTypeface(null, Typeface.BOLD);
        TextView sub = simpleText(subtitle, 12, R.color.cc_muted);
        sub.setPadding(0, dp(5), 0, 0);
        row.addView(titleView);
        row.addView(sub);
        if (!id.isEmpty()) {
            TextView delete = simpleText("Delete session", 12, R.color.cc_bad);
            delete.setGravity(Gravity.CENTER);
            delete.setPadding(dp(12), dp(10), dp(12), dp(8));
            delete.setOnClickListener(v -> confirmDeleteSession(id, title));
            LinearLayout.LayoutParams deleteLp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT);
            deleteLp.gravity = Gravity.END;
            row.addView(delete, deleteLp);
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

    private void createSession() {
        if (!serverHealthy) {
            toast("ClosedCode server is offline");
            refreshHealth();
            return;
        }
        toolStatus.setText("Creating session…");
        api.createSession(directory, "ClosedCode session", new ClosedCodeApi.Callback() {
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
        if (pageTransitionRunning) return;
        currentSessionId = id;
        connectionsPage.setVisibility(View.GONE);
        settingsPage.setVisibility(View.GONE);
        chatTitle.setText(title);
        chatWorkspace.setText(shortPath(directory));
        composerUi.openSession(id, directory);
        toolStatus.setText("Syncing…");
        loadMessages();
        startEventStream();
        refreshPendingInteractions();
        animateIntoSession();
    }

    private void animateIntoSession() {
        pageTransitionRunning = true;
        float width = Math.max(1f, getResources().getDisplayMetrics().widthPixels);
        sessionsPage.animate().cancel();
        chatPage.animate().cancel();

        chatPage.setVisibility(View.VISIBLE);
        chatPage.setTranslationX(width);
        chatPage.setAlpha(1f);
        bottomNav.setVisibility(View.GONE);

        sessionsPage.setVisibility(View.VISIBLE);
        sessionsPage.setTranslationX(0f);
        sessionsPage.setAlpha(1f);

        sessionsPage.animate()
                .translationX(-width * 0.18f)
                .alpha(0.86f)
                .setDuration(PAGE_TRANSITION_MS)
                .setInterpolator(PAGE_TRANSITION_INTERPOLATOR)
                .start();

        chatPage.animate()
                .translationX(0f)
                .setDuration(PAGE_TRANSITION_MS)
                .setInterpolator(PAGE_TRANSITION_INTERPOLATOR)
                .withEndAction(() -> {
                    sessionsPage.setVisibility(View.GONE);
                    sessionsPage.setTranslationX(0f);
                    sessionsPage.setAlpha(1f);
                    pageTransitionRunning = false;
                })
                .start();
    }

    private void closeChat() {
        if (pageTransitionRunning) return;
        clearTranscriptSelection(false);
        streamGeneration++;
        eventReconnectAttempt = 0;
        cancelActiveProviderForLifecycle();
        api.stopEvents();
        setPromptRunning(false);
        composerUi.closeSession();
        animateBackToSessions();
    }

    private void cancelActiveProviderForLifecycle() {
        final String requestId = activeProviderRequestId;
        activeProviderRequestId = null;
        providerStreamBody = null;
        passthroughSendActive = false;
        if (activeAgentPermissionDialog != null && activeAgentPermissionDialog.isShowing()) {
            activeAgentPermissionDialog.dismiss();
        }
        activeAgentPermissionDialog = null;
        pendingAgentPermissionExpectedId=null; pendingAgentPermissionRequestId=null; pendingAgentPermissionId=null; pendingAgentPermissionTool=null; pendingAgentPermissionArguments=null;
        interactionDialogOpen = false;
        if (requestId == null) return;
        api.cancelProviderRequest(requestId, new ClosedCodeApi.Callback() {
            @Override public void success(String body) { }
            @Override public void failure(String message) { }
        });
    }

    private void animateBackToSessions() {
        pageTransitionRunning = true;
        float width = Math.max(1f, getResources().getDisplayMetrics().widthPixels);
        sessionsPage.animate().cancel();
        chatPage.animate().cancel();

        sessionsPage.setVisibility(View.VISIBLE);
        sessionsPage.setTranslationX(-width * 0.18f);
        sessionsPage.setAlpha(0.86f);
        bottomNav.setVisibility(View.VISIBLE);
        tintNav("sessions");

        sessionsPage.animate()
                .translationX(0f)
                .alpha(1f)
                .setDuration(PAGE_TRANSITION_MS)
                .setInterpolator(PAGE_TRANSITION_INTERPOLATOR)
                .start();

        chatPage.animate()
                .translationX(width)
                .setDuration(PAGE_TRANSITION_MS)
                .setInterpolator(PAGE_TRANSITION_INTERPOLATOR)
                .withEndAction(() -> {
                    chatPage.setVisibility(View.GONE);
                    chatPage.setTranslationX(0f);
                    currentSessionId = null;
                    pageTransitionRunning = false;
                    refreshSessions();
                })
                .start();
    }

    private void loadMessages() {
        if (currentSessionId == null || passthroughSendActive) return;
        final String expectedId = currentSessionId;
        api.messages(expectedId, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                composerUi.onMessagesLoaded(body);
                renderMessages(body);
                if (isPassthroughProvider(composerUi.providerId())) {
                    loadPassthroughHistory(expectedId);
                } else {
                    toolStatus.setText("Idle");
                }
            }
            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Error");
                toast("Messages: " + message);
            }
        });
    }

    private void loadPassthroughHistory(String expectedId) {
        api.passthroughHistory(expectedId, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                try {
                    JSONObject root = new JSONObject(body);
                    JSONArray timeline=root.optJSONArray("timeline"), messages=root.optJSONArray("messages");
                    if (timeline!=null && timeline.length()>0) {
                        for(int i=0;i<timeline.length();i++) { JSONObject q=timeline.optJSONObject(i); if(q==null)continue;
                            if("tool".equals(q.optString("kind"))) addAgentToolBubble(q.optString("name","tool"),q.optString("status","completed"),q.optString("detail",""));
                            else { String c=q.optString("content",""); if(!c.trim().isEmpty()) addMessageBubble(q.optString("role",""),c); }
                        }
                    } else if(messages!=null) {
                        for(int i=0;i<messages.length();i++) { JSONObject q=messages.optJSONObject(i); if(q==null)continue; String c=q.optString("content",""); if(!c.trim().isEmpty()) addMessageBubble(q.optString("role",""),c); }
                    }
                    messageScroll.post(() -> messageScroll.fullScroll(View.FOCUS_DOWN));
                    toolStatus.setText("Idle");
                } catch (Exception e) {
                    toolStatus.setText("History error");
                }
            }

            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("History unavailable");
            }
        });
    }

    private void renderMessages(String body) {
        if (passthroughSendActive) {
            return;
        }
        clearTranscriptSelection(false);
        messageList.removeAllViews();
        try {
            JSONArray arr = new JSONArray(body);
            String lastRole = "";
            boolean lastAssistantCompleted = false;
            for (int i = 0; i < arr.length(); i++) {
                JSONObject item = arr.optJSONObject(i);
                if (item == null) continue;
                JSONObject info = item.optJSONObject("info");
                String role = info == null ? "" : info.optString("role", "");
                if (!role.isEmpty()) {
                    lastRole = role;
                    if ("assistant".equals(role)) {
                        JSONObject time = info.optJSONObject("time");
                        lastAssistantCompleted = time != null && time.has("completed");
                    }
                }
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
            if ("assistant".equals(lastRole) && lastAssistantCompleted) {
                setPromptRunning(false);
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
        registerTranscriptBlock(box);
    }

    private String readableToolActivity(String tool,String status) {
        String n=tool==null||tool.isEmpty()?"tool":tool, s=status==null||status.isEmpty()?"running":status;
        if("error".equals(s)) return "A workspace step failed: "+n; boolean d="completed".equals(s);
        if("workspace_read".equals(n)) return d?"Finished reading project context.":"Reading project context…";
        if(n.startsWith("workspace_")) return d?"Finished updating workspace files.":"Updating workspace files…";
        if("shell".equals(n)) return d?"Workspace command finished.":"Running a workspace command…";
        if(n.startsWith("git_")) return d?"Repository check finished.":"Checking repository state…";
        return d?"Finished "+n+".":"Working with "+n+"…";
    }

    private void addAgentToolBubble(String tool, String status, String detail) {
        String n=tool==null||tool.isEmpty()?"tool":tool, s=status==null||status.isEmpty()?"running":status;
        StringBuilder text=new StringBuilder();
        text.append(readableToolActivity(n,s)).append("\nTechnical: ⚙ ").append(n).append("  ·  ").append(s);
        if (detail != null && !detail.isEmpty()) text.append("\n").append(trim(detail, 180));
        TextView v = simpleText(text.toString(), 12, R.color.cc_muted);
        v.setBackgroundResource(R.drawable.bg_card);
        v.setPadding(dp(12), dp(10), dp(12), dp(10));
        messageList.addView(v, matchWrapMargins(0, 4, 36, 4));
        registerTranscriptBlock(v);
        toolStatus.setText(readableToolActivity(n,s));
        messageScroll.post(() -> messageScroll.fullScroll(View.FOCUS_DOWN));
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
        registerTranscriptBlock(v);
        toolStatus.setText(tool + " · " + status);
    }

    private void addActivityLine(String label, String detail) {
        String text = detail.isEmpty() ? label : label + " · " + trim(detail, 100);
        TextView v = simpleText(text, 11, R.color.cc_muted);
        v.setPadding(dp(8), dp(4), dp(8), dp(4));
        messageList.addView(v);
        registerTranscriptBlock(v);
    }

    private void registerTranscriptBlock(View block) {
        block.setClickable(true);
        block.setLongClickable(true);
        block.setOnLongClickListener(v -> {
            if (!transcriptSelectionMode) {
                transcriptSelectionMode = true;
                selectedTranscriptBlocks.clear();
            }
            toggleTranscriptSelection(block);
            return true;
        });
        block.setOnClickListener(v -> {
            if (transcriptSelectionMode) toggleTranscriptSelection(block);
        });
        if (block instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) block;
            for (int i = 0; i < group.getChildCount(); i++) {
                View child = group.getChildAt(i);
                child.setOnLongClickListener(v -> {
                    if (!transcriptSelectionMode) {
                        transcriptSelectionMode = true;
                        selectedTranscriptBlocks.clear();
                    }
                    toggleTranscriptSelection(block);
                    return true;
                });
                child.setOnClickListener(v -> {
                    if (transcriptSelectionMode) toggleTranscriptSelection(block);
                });
            }
        }
    }

    private void toggleTranscriptSelection(View block) {
        if (selectedTranscriptBlocks.contains(block)) {
            selectedTranscriptBlocks.remove(block);
            setTranscriptBlockSelected(block, false);
        } else {
            selectedTranscriptBlocks.add(block);
            setTranscriptBlockSelected(block, true);
        }
        transcriptSelectionMode = !selectedTranscriptBlocks.isEmpty();
        updateTranscriptSelectionUi();
    }

    private void setTranscriptBlockSelected(View block, boolean selected) {
        block.setAlpha(selected ? 0.55f : 1f);
        block.setScaleX(selected ? 0.985f : 1f);
        block.setScaleY(selected ? 0.985f : 1f);
    }

    private void clearTranscriptSelection(boolean announce) {
        for (View block : new ArrayList<>(selectedTranscriptBlocks)) {
            setTranscriptBlockSelected(block, false);
        }
        selectedTranscriptBlocks.clear();
        transcriptSelectionMode = false;
        updateTranscriptSelectionUi();
        if (announce) toolStatus.setText("Selection cleared");
    }

    private void updateTranscriptSelectionUi() {
        if (copySessionButton == null) return;
        int count = selectedTranscriptBlocks.size();
        copySessionButton.setText(count > 0 ? "Copy " + count : "Copy");
        copySessionButton.setContentDescription(
                count > 0 ? "Copy " + count + " selected transcript cards" : "Copy session transcript");
        if (count > 0 && toolStatus != null) toolStatus.setText(count + " selected");
    }

    private void copySessionTranscript() {
        if (currentSessionId == null || messageList == null) return;
        final boolean selectedOnly = transcriptSelectionMode && !selectedTranscriptBlocks.isEmpty();
        StringBuilder transcript = new StringBuilder();
        for (int i = 0; i < messageList.getChildCount(); i++) {
            View transcriptBlock = messageList.getChildAt(i);
            if (selectedOnly && !selectedTranscriptBlocks.contains(transcriptBlock)) continue;
            StringBuilder block = new StringBuilder();
            collectTranscriptText(transcriptBlock, block);
            String value = block.toString().trim();
            if (value.isEmpty()) continue;
            if (transcript.length() > 0) transcript.append("\n\n");
            transcript.append(value);
        }
        String text = transcript.toString().trim();
        if (text.isEmpty()) {
            toast("Nothing to copy");
            return;
        }
        android.content.ClipboardManager clipboard =
                (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        if (clipboard == null) {
            toast("Clipboard unavailable");
            return;
        }
        clipboard.setPrimaryClip(android.content.ClipData.newPlainText(
                selectedOnly ? "ClosedCode selection" : "ClosedCode session", text));
        int copiedCount = selectedTranscriptBlocks.size();
        if (selectedOnly) clearTranscriptSelection(false);
        toolStatus.setText(selectedOnly ? "Selection copied" : "Session copied");
        toast(selectedOnly ? copiedCount + " cards copied" : "Session copied");
    }

    private void collectTranscriptText(View view, StringBuilder out) {
        if (view instanceof TextView) {
            CharSequence value = ((TextView) view).getText();
            if (value != null) {
                String text = value.toString().trim();
                if (!text.isEmpty()) {
                    if (out.length() > 0) out.append("\n");
                    out.append(text);
                }
            }
            return;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                collectTranscriptText(group.getChildAt(i), out);
            }
        }
    }

    private void sendPrompt() {
        if (currentSessionId == null) return;
        String text = composer.getText().toString().trim();
        if (text.isEmpty()) return;
        if (promptRunning) {
            steerPrompt(text);
            return;
        }

        composer.setText("");
        final boolean passthroughPrompt = isPassthroughProvider(composerUi.providerId())
                && composerUi.modelId() != null
                && !composerUi.modelId().trim().isEmpty();
        if (passthroughPrompt) passthroughSendActive = true;
        addMessageBubble("user", text);
        final String expectedId = currentSessionId;
        final String currentTitle = chatTitle.getText().toString();
        final boolean backendDefaultTitle = currentTitle.startsWith("New session");
        final boolean closedCodePlaceholderTitle = currentTitle.startsWith("ClosedCode session");

        if (backendDefaultTitle || closedCodePlaceholderTitle) {
            String safeTitle = trim(text, 64);
            if (safeTitle.isEmpty()) safeTitle = "ClosedCode session";
            final String resolvedTitle = safeTitle;
            toolStatus.setText("Preparing session…");
            api.updateSessionTitle(expectedId, directory, resolvedTitle, new ClosedCodeApi.Callback() {
                @Override public void success(String body) {
                    if (!expectedId.equals(currentSessionId)) return;
                    chatTitle.setText(resolvedTitle);
                    dispatchPrompt(expectedId, text);
                }
                @Override public void failure(String message) {
                    if (!expectedId.equals(currentSessionId)) return;
                    if (backendDefaultTitle) {
                        passthroughSendActive = false;
                        composer.setText(text);
                        toolStatus.setText("Error");
                        addMessageBubble("system", "Unable to prepare this legacy session: " + message);
                        return;
                    }
                    dispatchPrompt(expectedId, text);
                }
            });
            return;
        }

        dispatchPrompt(expectedId, text);
    }

    private void dispatchPrompt(String expectedId, String text) {
        String providerId = composerUi.providerId();
        String modelId = composerUi.modelId();
        if (isPassthroughProvider(providerId) && modelId != null && !modelId.trim().isEmpty()) {
            dispatchPassthroughPrompt(expectedId, text, providerId, modelId);
            return;
        }

        passthroughSendActive = false;
        toolStatus.setText("Sending…");
        setPromptRunning(true);
        api.promptAsync(
                expectedId,
                directory,
                text,
                composerUi.providerId(),
                composerUi.modelId(),
                composerUi.agent(),
                composerUi.variant(),
                new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Running…");
                loadMessages();
                schedulePromptRefresh(expectedId, 450L);
                schedulePromptRefresh(expectedId, 1100L);
                schedulePromptRefresh(expectedId, 2200L);
                schedulePromptRefresh(expectedId, 4200L);
            }
            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                setPromptRunning(false);
                toolStatus.setText("Error");
                addMessageBubble("system", "Prompt failed: " + message);
            }
        });
    }

    private static boolean isPassthroughProvider(String providerId) {
        return "nvidia".equals(providerId) || "zai".equals(providerId);
    }

    private void dispatchPassthroughPrompt(String expectedId, String text, String providerId, String modelId) {
        String requestId = expectedId + "-" + System.nanoTime();
        activeProviderRequestId = requestId;
        providerStreamText.setLength(0);
        providerStreamBody = null;
        providerRunHadError = false;
        toolStatus.setText("Agent · " + providerId);
        setPromptRunning(true);
        api.streamAgentPrompt(
                expectedId,
                directory,
                text,
                providerId,
                modelId,
                prefs.getBoolean("fullAccessAutonomy", false) ? "full" : (prefs.getBoolean("yoloAutonomy", false) ? "yolo" : "ask"),
                requestId,
                new ClosedCodeApi.AgentStreamListener() {
                    @Override public void delta(String piece) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        if (providerStreamBody == null) {
                            providerStreamBody = addProviderStreamingBubble();
                        }
                        providerStreamText.append(piece);
                        providerStreamBody.setText(providerStreamText.toString());
                        messageScroll.post(() -> messageScroll.fullScroll(View.FOCUS_DOWN));
                    }

                    @Override public void tool(String name, String status, String detail) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        addAgentToolBubble(name, status, detail);
                    }

                    @Override public void permission(String permissionId, String name, String arguments) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        if (approveAllAgentRequests.contains(requestId) || isAgentActionAlwaysAllowed(name, arguments)) {
                            replyAgentPermission(expectedId, requestId, permissionId, true);
                            return;
                        }
                        showAgentPermission(expectedId, requestId, permissionId, name, arguments);
                    }

                    @Override public void error(String message) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        providerRunHadError = true;
                        toolStatus.setText("Agent error");
                        addMessageBubble("system", "Agent: " + message);
                        signalError(requestId, expectedId, chatTitle.getText().toString(), message);
                    }

                    @Override public void complete(boolean cancelled) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        approveAllAgentRequests.remove(requestId);
                        activeProviderRequestId = null;
                        providerStreamBody = null;
                        passthroughSendActive = false;
                        setPromptRunning(false);
                        toolStatus.setText(cancelled ? "Stopped" : "Agent complete");
                        if(!cancelled && !providerRunHadError) signalCompletion(requestId,expectedId,chatTitle.getText().toString(),providerId,modelId);
                    }

                    @Override public void failure(String message) {
                        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
                        approveAllAgentRequests.remove(requestId);
                        activeProviderRequestId = null;
                        providerStreamBody = null;
                        passthroughSendActive = false;
                        setPromptRunning(false);
                        toolStatus.setText("Agent unavailable");
                        addMessageBubble("system", "Agent failed: " + message);
                        signalError(requestId, expectedId, chatTitle.getText().toString(), message);
                    }
                });
    }

    private boolean isWorkspaceScopedApprovalTool(String tool) {
        return "workspace_write".equals(tool) || "workspace_patch".equals(tool)
                || "workspace_mkdir".equals(tool) || "workspace_move".equals(tool)
                || "workspace_delete".equals(tool);
    }

    private String approvalWorkspaceKey() {
        return directory == null ? "" : directory.trim();
    }

    private String legacyAgentApprovalKey(String tool, String arguments) {
        return (tool == null ? "" : tool) + "\u001f" + (arguments == null ? "{}" : arguments);
    }

    private String agentApprovalKey(String tool, String arguments) {
        String safeTool = tool == null ? "" : tool;
        if (isWorkspaceScopedApprovalTool(safeTool)) {
            return "workspace\u001f" + approvalWorkspaceKey() + "\u001f" + safeTool;
        }
        return "exact\u001f" + approvalWorkspaceKey() + "\u001f" + safeTool + "\u001f"
                + (arguments == null ? "{}" : arguments);
    }

    private boolean isAgentActionAlwaysAllowed(String tool, String arguments) {
        java.util.Set<String> saved = prefs.getStringSet("agentAlwaysAllowedActions", java.util.Collections.emptySet());
        return saved != null && (saved.contains(agentApprovalKey(tool, arguments))
                || saved.contains(legacyAgentApprovalKey(tool, arguments)));
    }

    private void rememberAgentActionAlwaysAllowed(String tool, String arguments) {
        java.util.Set<String> saved = prefs.getStringSet("agentAlwaysAllowedActions", java.util.Collections.emptySet());
        java.util.HashSet<String> updated = new java.util.HashSet<>();
        if (saved != null) updated.addAll(saved);
        updated.add(agentApprovalKey(tool, arguments));
        prefs.edit().putStringSet("agentAlwaysAllowedActions", updated).apply();
    }

    private void queueAgentPermission(String expectedId,String requestId,String permissionId,String tool,String arguments) {
        pendingAgentPermissionExpectedId=expectedId;
        pendingAgentPermissionRequestId=requestId;
        pendingAgentPermissionId=permissionId;
        pendingAgentPermissionTool=tool;
        pendingAgentPermissionArguments=arguments;
        toolStatus.setText("Permission waiting…");
    }

    private void showPendingAgentPermissionIfAny() {
        if (interactionDialogOpen || pendingAgentPermissionId==null) return;
        String expectedId=pendingAgentPermissionExpectedId, requestId=pendingAgentPermissionRequestId, permissionId=pendingAgentPermissionId, tool=pendingAgentPermissionTool, arguments=pendingAgentPermissionArguments;
        pendingAgentPermissionExpectedId=null; pendingAgentPermissionRequestId=null; pendingAgentPermissionId=null; pendingAgentPermissionTool=null; pendingAgentPermissionArguments=null;
        showAgentPermission(expectedId,requestId,permissionId,tool,arguments);
    }

    private void finishInteractionDialog() {
        interactionDialogOpen=false;
        activeAgentPermissionDialog=null;
        if (pendingAgentPermissionId!=null) showPendingAgentPermissionIfAny();
        else refreshPendingInteractions();
    }

    private android.widget.Button agentPermissionButton(String label) {
        android.widget.Button button=new android.widget.Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setTextSize(15);
        button.setMinHeight(dp(48));
        return button;
    }

    private void showAgentPermission(String expectedId,String requestId,String permissionId,String tool,String arguments) {
        if (!expectedId.equals(currentSessionId) || !requestId.equals(activeProviderRequestId)) return;
        if (interactionDialogOpen) {
            queueAgentPermission(expectedId,requestId,permissionId,tool,arguments);
            return;
        }
        interactionDialogOpen=true;
        LinearLayout panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(20),dp(4),dp(20),dp(12));
        TextView detail=simpleText(tool+"\n\n"+trim(arguments,500),14,R.color.cc_text);
        detail.setTextIsSelectable(true);
        panel.addView(detail,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        android.widget.Button once=agentPermissionButton("Allow once");
        android.widget.Button all=agentPermissionButton("Approve all for this task");
        String persistentLabel=isWorkspaceScopedApprovalTool(tool) ? "Always allow this tool in this workspace" : "Always allow this exact command";
        android.widget.Button always=agentPermissionButton(persistentLabel);
        android.widget.Button reject=agentPermissionButton("Reject");
        panel.addView(once); panel.addView(all); panel.addView(always); panel.addView(reject);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Allow agent tool?").setView(panel).create();
        dialog.setCancelable(false);
        once.setOnClickListener(v->{ dialog.dismiss(); replyAgentPermission(expectedId,requestId,permissionId,true); });
        all.setOnClickListener(v->{ approveAllAgentRequests.add(requestId); dialog.dismiss(); replyAgentPermission(expectedId,requestId,permissionId,true); });
        always.setOnClickListener(v->{ rememberAgentActionAlwaysAllowed(tool,arguments); dialog.dismiss(); replyAgentPermission(expectedId,requestId,permissionId,true); });
        reject.setOnClickListener(v->{ dialog.dismiss(); replyAgentPermission(expectedId,requestId,permissionId,false); });
        dialog.setOnDismissListener(d->finishInteractionDialog());
        activeAgentPermissionDialog=dialog;
        dialog.show();
    }

    private void replyAgentPermission(String expectedId,String requestId,String permissionId,boolean allow) {
        api.replyAgentPermission(requestId,permissionId,allow,new ClosedCodeApi.Callback(){
            @Override public void success(String body){
                if(!expectedId.equals(currentSessionId)) return;
                try{ JSONObject result=new JSONObject(body); if(!result.optBoolean("resolved",false)){ toolStatus.setText("Permission expired"); toast("That permission prompt expired before the reply arrived"); return; } }
                catch(Exception e){ toolStatus.setText("Permission reply invalid"); toast("Agent permission returned an invalid response"); return; }
                toolStatus.setText(allow ? "Agent tool allowed" : "Agent tool rejected");
            }
            @Override public void failure(String message){ if(!expectedId.equals(currentSessionId)) return; toolStatus.setText("Permission reply failed"); toast("Agent permission: "+message); }
        });
    }

    private TextView addProviderStreamingBubble() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(12), dp(10), dp(12), dp(10));
        TextView tag = simpleText("CLOSEDCODE", 10, R.color.cc_muted);
        tag.setTypeface(null, Typeface.BOLD);
        TextView body = simpleText("", 15, R.color.cc_text);
        body.setPadding(0, dp(6), 0, 0);
        body.setTextIsSelectable(true);
        box.addView(tag);
        box.addView(body);
        messageList.addView(box, matchWrapMargins(0, 5, 20, 5));
        registerTranscriptBlock(box);
        messageScroll.post(() -> messageScroll.fullScroll(View.FOCUS_DOWN));
        return body;
    }

    private void steerPrompt(String text) {
        final String expectedId = currentSessionId;
        final String requestId = activeProviderRequestId;
        if (expectedId == null || requestId == null) {
            toolStatus.setText("Steering unavailable");
            toast("Steering is available for active provider-agent tasks");
            return;
        }
        composer.setText("");
        toolStatus.setText("Steering…");
        api.steerAgentRequest(requestId, text, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                addMessageBubble("user", text);
                toolStatus.setText(requestId.equals(activeProviderRequestId) ? "Steering queued…" : "Steering saved");
            }

            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                if (composer.getText().toString().trim().isEmpty()) composer.setText(text);
                toolStatus.setText("Steering failed");
                addMessageBubble("system", "Steering failed: " + message);
            }
        });
    }

    private void abortPrompt() {
        if (currentSessionId == null) return;
        final String expectedId = currentSessionId;
        final String providerRequestId = activeProviderRequestId;
        toolStatus.setText("Stopping…");
        if (providerRequestId != null) {
            api.cancelProviderRequest(providerRequestId, new ClosedCodeApi.Callback() {
                @Override public void success(String body) {
                    if (!expectedId.equals(currentSessionId)) return;
                    toolStatus.setText("Stopping provider…");
                }
                @Override public void failure(String message) {
                    if (!expectedId.equals(currentSessionId)) return;
                    toolStatus.setText("Stop failed");
                    toast("Provider stop: " + message);
                }
            });
            return;
        }
        api.abort(expectedId, directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                if (!expectedId.equals(currentSessionId)) return;
                setPromptRunning(false);
                toolStatus.setText("Stopped");
                loadMessages();
            }
            @Override public void failure(String message) {
                if (!expectedId.equals(currentSessionId)) return;
                toolStatus.setText("Stop failed");
                toast("Stop: " + message);
            }
        });
    }

    private void setPromptRunning(boolean running) {
        promptRunning = running;
        if (sendButton != null) {
            sendButton.setText("↑");
            sendButton.setContentDescription(running ? "Steer active task" : "Send prompt");
        }
        if (stopButton != null) {
            stopButton.setVisibility(running ? View.VISIBLE : View.GONE);
            stopButton.setEnabled(running);
            stopButton.setContentDescription("Stop generation");
        }
    }

    private void schedulePromptRefresh(String expectedId, long delayMs) {
        composer.postDelayed(() -> {
            if (expectedId.equals(currentSessionId)) {
                loadMessages();
                refreshPendingInteractions();
            }
        }, delayMs);
    }

    private void startEventStream() {
        startEventStream(true);
    }

    private void startEventStream(boolean resetBackoff) {
        if (resetBackoff) eventReconnectAttempt = 0;
        final int generation = ++streamGeneration;
        api.startEvents(directory, new ClosedCodeApi.EventListener() {
            @Override public void event(String data) {
                if (generation != streamGeneration || currentSessionId == null) return;
                eventReconnectAttempt = 0;
                if (data.contains(currentSessionId) || data.contains("message") || data.contains("session")) {
                    toolStatus.setText("Live");
                    loadMessages();
                    refreshPendingInteractions();
                }
                if (data.contains("permission") || data.contains("question")) refreshPendingInteractions();
                if (data.contains("error") && data.contains(currentSessionId)) {
                    setPromptRunning(false);
                }
            }
            @Override public void closed(String reason) {
                if (generation != streamGeneration || currentSessionId == null) return;
                int attempt = ++eventReconnectAttempt;
                long delay = Math.min(8000L, 500L << Math.min(attempt - 1, 4));
                toolStatus.setText("Reconnecting…");
                composer.postDelayed(() -> {
                    if (generation == streamGeneration && currentSessionId != null) {
                        startEventStream(false);
                    }
                }, delay);
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
        dialog.setOnDismissListener(d -> finishInteractionDialog());
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

    private void showFiles(String path) {
        api.workspaceList(directory, path, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject root = new JSONObject(body);
                    JSONArray arr = root.optJSONArray("items");
                    if (arr == null) arr = new JSONArray();
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
                        if (node == null) continue;
                        nodes.add(node);
                        labels.add(("directory".equals(node.optString("type")) ? "▸  " : "   ")
                                + node.optString("name", node.optString("path")));
                    }
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle("Files · " + path)
                            .setItems(labels.toArray(new String[0]), (dialog, which) -> {
                                JSONObject node = nodes.get(which);
                                String nodePath = node.optString("path", ".");
                                if ("directory".equals(node.optString("type"))) showFiles(nodePath);
                                else showFile(nodePath);
                            })
                            .setPositiveButton("New", (dialog, which) -> showCreateEntry(path))
                            .setNeutralButton("Search", (dialog, which) -> showWorkspaceSearch())
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
        api.workspaceRead(directory, path, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject obj = new JSONObject(body);
                    String content = obj.optString("content", "");
                    EditText editor = new EditText(MainActivity.this);
                    editor.setText(content);
                    editor.setTextColor(getColor(R.color.cc_text));
                    editor.setTextSize(12);
                    editor.setGravity(Gravity.TOP | Gravity.START);
                    editor.setMinLines(12);
                    editor.setPadding(dp(14), dp(12), dp(14), dp(12));
                    editor.setHorizontallyScrolling(false);
                    ScrollView scroll = new ScrollView(MainActivity.this);
                    scroll.setBackgroundColor(getColor(R.color.cc_bg));
                    scroll.addView(editor);
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle(path)
                            .setView(scroll)
                            .setPositiveButton("Save", (dialog, which) ->
                                    saveWorkspaceFile(path, editor.getText().toString()))
                            .setNegativeButton("Close", null)
                            .show();
                } catch (Exception e) {
                    toast("Read: " + e.getMessage());
                }
            }
            @Override public void failure(String message) { toast("Read: " + message); }
        });
    }

    private void saveWorkspaceFile(String path, String content) {
        toolStatus.setText("Saving…");
        api.workspaceWrite(directory, path, content, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                toolStatus.setText("Saved");
                toast("Saved " + path);
            }
            @Override public void failure(String message) {
                toolStatus.setText("Save failed");
                toast("Save: " + message);
            }
        });
    }

    private void showCreateEntry(String parent) {
        EditText input = new EditText(this);
        input.setHint("name");
        new AlertDialog.Builder(this)
                .setTitle("Create in " + parent)
                .setView(input)
                .setPositiveButton("File", (dialog, which) -> {
                    String name = input.getText().toString().trim();
                    if (name.isEmpty()) return;
                    String path = childPath(parent, name);
                    api.workspaceWrite(directory, path, "", new ClosedCodeApi.Callback() {
                        @Override public void success(String body) {
                            toast("Created " + path);
                            showFile(path);
                        }
                        @Override public void failure(String message) { toast("Create file: " + message); }
                    });
                })
                .setNeutralButton("Folder", (dialog, which) -> {
                    String name = input.getText().toString().trim();
                    if (name.isEmpty()) return;
                    String path = childPath(parent, name);
                    api.workspaceMkdir(directory, path, new ClosedCodeApi.Callback() {
                        @Override public void success(String body) {
                            toast("Created " + path);
                            showFiles(path);
                        }
                        @Override public void failure(String message) { toast("Create folder: " + message); }
                    });
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showWorkspaceSearch() {
        EditText input = new EditText(this);
        input.setHint("Search project files");
        new AlertDialog.Builder(this)
                .setTitle("Workspace search")
                .setView(input)
                .setPositiveButton("Search", (dialog, which) -> {
                    String query = input.getText().toString().trim();
                    if (!query.isEmpty()) runWorkspaceSearch(query);
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void runWorkspaceSearch(String query) {
        toolStatus.setText("Searching…");
        api.workspaceSearch(directory, query, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject root = new JSONObject(body);
                    JSONArray results = root.optJSONArray("results");
                    if (results == null || results.length() == 0) {
                        toolStatus.setText("Idle");
                        toast("No matches for " + query);
                        return;
                    }
                    String[] labels = new String[results.length()];
                    String[] paths = new String[results.length()];
                    for (int i = 0; i < results.length(); i++) {
                        JSONObject item = results.optJSONObject(i);
                        if (item == null) continue;
                        paths[i] = item.optString("path", "");
                        int line = item.optInt("line", 0);
                        String preview = item.optString("preview", "");
                        labels[i] = paths[i] + (line > 0 ? ":" + line : "") + "\n" + trim(preview, 100);
                    }
                    toolStatus.setText("Idle");
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle("Search · " + query)
                            .setItems(labels, (dialog, which) -> {
                                if (paths[which] != null && !paths[which].isEmpty()) showFile(paths[which]);
                            })
                            .setNegativeButton("Close", null)
                            .show();
                } catch (Exception e) {
                    toolStatus.setText("Search error");
                    toast("Search: " + e.getMessage());
                }
            }
            @Override public void failure(String message) {
                toolStatus.setText("Search failed");
                toast("Search: " + message);
            }
        });
    }

    private String childPath(String parent, String name) {
        if (parent == null || parent.isEmpty() || ".".equals(parent)) return name;
        return parent.endsWith("/") ? parent + name : parent + "/" + name;
    }

    private void showRunCommand() {
        if (interactionDialogOpen) {
            toast("Finish the current interaction first");
            return;
        }
        EditText input = new EditText(this);
        input.setHint("Command");
        input.setSingleLine(false);
        input.setMinLines(2);
        interactionDialogOpen = true;
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Run in " + shortPath(directory))
                .setMessage("Runs through the ClosedCode Termux command path.")
                .setView(input)
                .setPositiveButton("Run", (d, which) -> {
                    String command = input.getText().toString();
                    if (!command.trim().isEmpty()) runWorkspaceCommand(command);
                })
                .setNegativeButton("Cancel", null)
                .create();
        dialog.setOnDismissListener(d -> finishInteractionDialog());
        dialog.show();
    }

    private void runWorkspaceCommand(String command) {
        toolStatus.setText("Running command…");
        api.runCommand(directory, ".", command, 60, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    JSONObject result = new JSONObject(body);
                    StringBuilder output = new StringBuilder();
                    output.append("cwd: ").append(result.optString("cwd", ".")).append("\n");
                    if (result.optBoolean("timedOut", false)) output.append("timed out\n");
                    else output.append("exit: ").append(result.optString("exitCode", "null")).append("\n");
                    output.append("duration: ").append(result.optLong("durationMs", 0)).append(" ms\n");
                    String stdout = result.optString("stdout", "");
                    String stderr = result.optString("stderr", "");
                    if (!stdout.isEmpty()) output.append("\nstdout\n").append(stdout);
                    if (!stderr.isEmpty()) output.append("\nstderr\n").append(stderr);
                    if (result.optBoolean("stdoutTruncated", false)) output.append("\n[stdout truncated]");
                    if (result.optBoolean("stderrTruncated", false)) output.append("\n[stderr truncated]");
                    TextView text = simpleText(output.toString(), 12, R.color.cc_text);
                    text.setTextIsSelectable(true);
                    text.setPadding(dp(16), dp(10), dp(16), dp(10));
                    ScrollView scroll = new ScrollView(MainActivity.this);
                    scroll.setBackgroundColor(getColor(R.color.cc_bg));
                    scroll.addView(text);
                    toolStatus.setText("Command complete");
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle("Command result")
                            .setView(scroll)
                            .setPositiveButton("Done", null)
                            .show();
                } catch (Exception e) {
                    toolStatus.setText("Command parse error");
                    toast("Command: " + e.getMessage());
                }
            }
            @Override public void failure(String message) {
                toolStatus.setText("Command failed");
                toast("Command: " + message);
            }
        });
    }

    private void showDiff() {
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
                        if (!status.isEmpty()) out.append("status\n").append(status);
                        if (!diff.isEmpty()) {
                            if (out.length() > 0) out.append("\n");
                            out.append("diff\n").append(diff);
                        }
                        if (result.optBoolean("statusTruncated", false)) out.append("\n[status truncated]");
                        if (result.optBoolean("diffTruncated", false)) out.append("\n[diff truncated]");
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

    private android.net.Uri completionSoundUri(){
        String saved=prefs==null?null:prefs.getString("completionSoundUri",null);
        if(saved!=null&&!saved.isEmpty()) try{return android.net.Uri.parse(saved);}catch(Exception ignored){}
        return android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_NOTIFICATION);
    }
    private void updateCompletionSoundUi(){
        if(completionSoundToggle==null)return;
        boolean enabled=prefs.getBoolean("completionSoundEnabled",true);
        completionSoundToggle.setText(enabled?"🔊":"🔇");
        completionSoundToggle.setContentDescription(enabled?"Mute completion sound":"Unmute completion sound");
        try{ android.media.Ringtone q=android.media.RingtoneManager.getRingtone(this,completionSoundUri()); String title=q==null?"Default notification":q.getTitle(this); completionSoundLabel.setText("Sound: "+title); }catch(Exception e){ completionSoundLabel.setText("Sound: Default notification"); }
    }
    private void chooseCompletionSound(){
        Intent i=new Intent(android.media.RingtoneManager.ACTION_RINGTONE_PICKER);
        i.putExtra(android.media.RingtoneManager.EXTRA_RINGTONE_TYPE,android.media.RingtoneManager.TYPE_NOTIFICATION);
        i.putExtra(android.media.RingtoneManager.EXTRA_RINGTONE_SHOW_DEFAULT,true);
        i.putExtra(android.media.RingtoneManager.EXTRA_RINGTONE_SHOW_SILENT,false);
        i.putExtra(android.media.RingtoneManager.EXTRA_RINGTONE_EXISTING_URI,completionSoundUri());
        startActivityForResult(i,SOUND_REQUEST_CODE);
    }
    private void playCompletionSound(boolean force){
        if(!force && !prefs.getBoolean("completionSoundEnabled",true))return;
        try{ android.media.Ringtone q=android.media.RingtoneManager.getRingtone(this,completionSoundUri()); if(q!=null)q.play(); else toast("Completion sound unavailable"); }catch(Exception e){ toast("Completion sound failed: "+e.getMessage()); }
    }
    private void ensureCompletionChannel(){
        android.app.NotificationManager n=(android.app.NotificationManager)getSystemService(NOTIFICATION_SERVICE); if(n==null)return;
        android.app.NotificationChannel c=new android.app.NotificationChannel(COMPLETION_CHANNEL_ID,"Agent completions",android.app.NotificationManager.IMPORTANCE_DEFAULT);
        c.setDescription("Successful ClosedCode agent completions");
        c.setSound(android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_NOTIFICATION),null); n.createNotificationChannel(c);
        android.app.NotificationChannel e=new android.app.NotificationChannel(ERROR_CHANNEL_ID,"Agent errors",android.app.NotificationManager.IMPORTANCE_DEFAULT);
        e.setDescription("ClosedCode agent failures and errors");
        e.setSound(android.media.RingtoneManager.getDefaultUri(android.media.RingtoneManager.TYPE_NOTIFICATION),null); n.createNotificationChannel(e);
    }
    private void requestCompletionPermission(){
        if(android.os.Build.VERSION.SDK_INT>=33 && prefs!=null && (prefs.getBoolean("notifyCompleted",true)||prefs.getBoolean("notifyErrors",true)) && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS},914);
    }
    private void signalCompletion(String rid,String sid,String title,String provider,String model){
        if(prefs==null||rid==null||rid.equals(lastCompletionAlertRequestId))return; lastCompletionAlertRequestId=rid;
        if(appVisible){ playCompletionSound(false); return; }
        if(!prefs.getBoolean("notifyCompleted",true))return;
        if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
        int notificationId=("complete|"+sid+"|"+rid).hashCode();
        Intent i=new Intent(this,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP).putExtra("cc.sid",sid).putExtra("cc.title",title);
        android.app.PendingIntent p=android.app.PendingIntent.getActivity(this,notificationId,i,android.app.PendingIntent.FLAG_UPDATE_CURRENT|android.app.PendingIntent.FLAG_IMMUTABLE);
        android.app.Notification n=new android.app.Notification.Builder(this,COMPLETION_CHANNEL_ID).setSmallIcon(android.R.drawable.stat_sys_download_done).setContentTitle("ClosedCode · Agent complete").setContentText((title==null||title.isEmpty()?"Session complete":title)+" · "+provider+" · "+model).setContentIntent(p).setAutoCancel(true).build();
        android.app.NotificationManager nm=(android.app.NotificationManager)getSystemService(NOTIFICATION_SERVICE); if(nm!=null)nm.notify(notificationId,n);
    }
    private void signalError(String rid,String sid,String title,String message){
        if(prefs==null||rid==null||rid.equals(lastErrorAlertRequestId)||!prefs.getBoolean("notifyErrors",true))return; lastErrorAlertRequestId=rid;
        if(android.os.Build.VERSION.SDK_INT>=33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
        int notificationId=("error|"+sid+"|"+rid).hashCode();
        Intent i=new Intent(this,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP).putExtra("cc.sid",sid).putExtra("cc.title",title);
        android.app.PendingIntent p=android.app.PendingIntent.getActivity(this,notificationId,i,android.app.PendingIntent.FLAG_UPDATE_CURRENT|android.app.PendingIntent.FLAG_IMMUTABLE);
        String detail=message==null||message.isEmpty()?"Agent task failed":trim(message,180);
        android.app.Notification n=new android.app.Notification.Builder(this,ERROR_CHANNEL_ID).setSmallIcon(android.R.drawable.stat_notify_error).setContentTitle("ClosedCode · Agent error").setContentText(detail).setContentIntent(p).setAutoCancel(true).build();
        android.app.NotificationManager nm=(android.app.NotificationManager)getSystemService(NOTIFICATION_SERVICE); if(nm!=null)nm.notify(notificationId,n);
    }
    private void handleCompletionIntent(Intent i){ if(i==null)return; String sid=i.getStringExtra("cc.sid"); if(sid==null||sid.isEmpty()||sid.equals(currentSessionId))return; String t=i.getStringExtra("cc.title"); openSession(sid,t==null?"ClosedCode session":t); }
    @Override protected void onStart(){super.onStart();appVisible=true;}
    @Override protected void onStop(){appVisible=false;super.onStop();}
    @Override protected void onNewIntent(Intent i){super.onNewIntent(i);setIntent(i);handleCompletionIntent(i);}

    @Override protected void onDestroy() {
        streamGeneration++;
        cancelActiveProviderForLifecycle();
        api.shutdown();
        super.onDestroy();
    }
}
