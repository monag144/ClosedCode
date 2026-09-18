package com.monag.closedcode.mobile;

import android.app.Activity;
import android.content.SharedPreferences;
import android.text.TextUtils;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.DateFormat;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public final class ComposerUiController {
    private static final String DEFAULT_AGENT = "build";

    private final Activity activity;
    private final ClosedCodeApi api;
    private final SharedPreferences prefs;
    private final TextView modelChip;
    private final TextView agentChip;
    private final TextView effortChip;
    private final ContextUsageView usageView;

    private String directory;
    private String sessionId;
    private String selectedProviderId;
    private String selectedModelId;
    private String selectedAgent = DEFAULT_AGENT;
    private String selectedVariant;
    private String lastMessagesBody = "[]";

    private final List<AgentChoice> agents = new ArrayList<>();
    private final List<ProviderChoice> providers = new ArrayList<>();
    private final Map<String, String> providerDefaults = new HashMap<>();

    private static final class AgentChoice {
        final String name;
        final String mode;
        final String providerId;
        final String modelId;
        final String variant;

        AgentChoice(String name, String mode, String providerId, String modelId, String variant) {
            this.name = name;
            this.mode = mode;
            this.providerId = providerId;
            this.modelId = modelId;
            this.variant = variant;
        }
    }

    private static final class ModelChoice {
        final String id;
        final String name;
        final String status;
        final boolean reasoning;
        final long contextLimit;
        final List<String> variants = new ArrayList<>();

        ModelChoice(String id, String name, String status, boolean reasoning, long contextLimit) {
            this.id = id;
            this.name = name;
            this.status = status;
            this.reasoning = reasoning;
            this.contextLimit = contextLimit;
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

    private static final class UsageSnapshot {
        int all;
        int user;
        int assistant;
        String providerId = "";
        String modelId = "";
        String providerLabel = "—";
        String modelLabel = "—";
        long limit;
        long input;
        long output;
        long reasoning;
        long cacheRead;
        long cacheWrite;
        long total;
        int usage;
        long lastActivity;
        boolean hasUsage;
    }

    public ComposerUiController(
            Activity activity,
            ClosedCodeApi api,
            SharedPreferences prefs,
            TextView modelChip,
            TextView agentChip,
            TextView effortChip,
            ContextUsageView usageView,
            String directory) {
        this.activity = activity;
        this.api = api;
        this.prefs = prefs;
        this.modelChip = modelChip;
        this.agentChip = agentChip;
        this.effortChip = effortChip;
        this.usageView = usageView;
        this.directory = directory;
        restoreSelectionKeys();
        updateLabels();
        usageView.setPercentage(0);
    }

    public void refresh(String directory) {
        this.directory = directory;
        refreshAgents();
        refreshProviders();
    }

    public void openSession(String sessionId, String directory) {
        this.sessionId = sessionId;
        this.directory = directory;
        this.lastMessagesBody = "[]";
        usageView.setPercentage(0);
        restoreSelectionKeys();
        reconcileAgent();
        reconcileModel();
        updateLabels();
        refresh(directory);
    }

    public void closeSession() {
        sessionId = null;
        lastMessagesBody = "[]";
        usageView.setPercentage(0);
    }

    public String providerId() {
        return selectedProviderId;
    }

    public String modelId() {
        return selectedModelId;
    }

    public String agent() {
        return selectedAgent;
    }

    public String variant() {
        return selectedVariant;
    }

    public void showAgentPicker() {
        if (agents.isEmpty()) {
            toast("Agent catalog is still loading");
            refreshAgents();
            return;
        }
        ArrayList<OpenCodeSheet.Choice> rows = new ArrayList<>();
        for (AgentChoice agent : agents) {
            rows.add(new OpenCodeSheet.Choice(
                    agent.name,
                    displayName(agent.name),
                    "primary".equals(agent.mode) ? "Primary agent" : agent.mode,
                    ""));
        }
        OpenCodeSheet.showChoices(
                activity,
                agentChip,
                "Agent mode",
                "Choose how OpenCode should work in this session.",
                rows,
                selectedAgent,
                choice -> {
                    AgentChoice agent = findAgent(choice.id);
                    if (agent == null) return;
                    selectedAgent = agent.name;
                    if (!TextUtils.isEmpty(agent.providerId) && !TextUtils.isEmpty(agent.modelId)) {
                        ProviderChoice provider = findProvider(agent.providerId);
                        ModelChoice model = findModel(provider, agent.modelId);
                        if (provider != null && provider.connected && model != null) {
                            applyModel(provider, model, false);
                        }
                    }
                    if (!TextUtils.isEmpty(agent.variant)) {
                        ModelChoice current = currentModel();
                        if (current != null && current.variants.contains(agent.variant)) selectedVariant = agent.variant;
                    }
                    persistAgent();
                    persistModelAndVariant();
                    updateLabels();
                });
    }

    public void showModelPicker() {
        ArrayList<OpenCodeSheet.Choice> rows = new ArrayList<>();
        ArrayList<ProviderChoice> connected = new ArrayList<>();
        for (ProviderChoice provider : providers) if (provider.connected) connected.add(provider);
        connected.sort(Comparator.comparing(p -> p.name.toLowerCase(Locale.ROOT)));

        for (ProviderChoice provider : connected) {
            ArrayList<ModelChoice> models = new ArrayList<>(provider.models);
            models.sort(Comparator.comparing(m -> m.name.toLowerCase(Locale.ROOT)));
            for (ModelChoice model : models) {
                if ("deprecated".equalsIgnoreCase(model.status)) continue;
                rows.add(new OpenCodeSheet.Choice(
                        modelKey(provider.id, model.id),
                        model.name,
                        model.id,
                        provider.name));
            }
        }

        if (rows.isEmpty()) {
            toast("No connected models are available");
            refreshProviders();
            return;
        }

        OpenCodeSheet.showSearchChoices(
                activity,
                modelChip,
                "Select Model",
                "Search connected models by provider, name, or model ID.",
                rows,
                modelKey(selectedProviderId, selectedModelId),
                choice -> {
                    String[] ids = splitModelKey(choice.id);
                    ProviderChoice provider = findProvider(ids[0]);
                    ModelChoice model = findModel(provider, ids[1]);
                    if (provider == null || !provider.connected || model == null) return;
                    applyModel(provider, model, true);
                });
    }

    public void showEffortPicker() {
        ModelChoice model = currentModel();
        ArrayList<OpenCodeSheet.Choice> rows = new ArrayList<>();
        rows.add(new OpenCodeSheet.Choice(
                "",
                "Default",
                "Use model default reasoning",
                ""));

        if (model != null) {
            for (String variant : model.variants) {
                rows.add(new OpenCodeSheet.Choice(
                        variant,
                        displayName(variant),
                        model.name,
                        ""));
            }
        }

        OpenCodeSheet.showChoices(
                activity,
                effortChip,
                "Reasoning Effort",
                model == null ? "Select a model to load its reasoning variants." : "Variants reported by " + model.name,
                rows,
                selectedVariant == null ? "" : selectedVariant,
                choice -> {
                    selectedVariant = choice.id.isEmpty() ? null : choice.id;
                    persistVariant();
                    updateLabels();
                });
    }

    public void showUsage() {
        if (sessionId == null) return;
        api.listSessions(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                JSONObject session = findSession(body, sessionId);
                if (session == null) {
                    toast("Session details are unavailable");
                    return;
                }
                if ("[]".equals(lastMessagesBody)) {
                    api.messages(sessionId, directory, new ClosedCodeApi.Callback() {
                        @Override public void success(String messages) {
                            onMessagesLoaded(messages);
                            showUsageSheet(session, messages);
                        }
                        @Override public void failure(String message) {
                            showUsageSheet(session, "[]");
                        }
                    });
                    return;
                }
                showUsageSheet(session, lastMessagesBody);
            }

            @Override public void failure(String message) {
                toast("Usage: " + message);
            }
        });
    }

    public void onMessagesLoaded(String body) {
        lastMessagesBody = body == null ? "[]" : body;
        UsageSnapshot snapshot = computeUsage(lastMessagesBody);
        usageView.setPercentage(snapshot.usage);
    }

    private void refreshAgents() {
        api.listAgents(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                agents.clear();
                try {
                    JSONArray array = new JSONArray(body);
                    for (int i = 0; i < array.length(); i++) {
                        JSONObject agent = array.optJSONObject(i);
                        if (agent == null) continue;
                        if ("subagent".equals(agent.optString("mode"))) continue;
                        if (agent.optBoolean("hidden", false)) continue;
                        String name = agent.optString("name", "");
                        if (name.isEmpty()) continue;
                        JSONObject model = agent.optJSONObject("model");
                        agents.add(new AgentChoice(
                                name,
                                agent.optString("mode", "primary"),
                                model == null ? "" : model.optString("providerID", ""),
                                model == null ? "" : model.optString("modelID", ""),
                                nullableString(agent, "variant")));
                    }
                } catch (Exception ignored) {
                    agents.clear();
                }
                reconcileAgent();
                updateLabels();
            }

            @Override public void failure(String message) {
                agents.clear();
                updateLabels();
            }
        });
    }

    private void refreshProviders() {
        api.listProviders(directory, new ClosedCodeApi.Callback() {
            @Override public void success(String body) {
                try {
                    parseProviders(new JSONObject(body));
                    reconcileModel();
                } catch (Exception e) {
                    providers.clear();
                    providerDefaults.clear();
                }
                updateLabels();
                onMessagesLoaded(lastMessagesBody);
            }

            @Override public void failure(String message) {
                providers.clear();
                providerDefaults.clear();
                updateLabels();
            }
        });
    }

    private void parseProviders(JSONObject root) {
        providers.clear();
        providerDefaults.clear();

        Set<String> connected = new HashSet<>();
        JSONArray connectedArray = root.optJSONArray("connected");
        if (connectedArray != null) {
            for (int i = 0; i < connectedArray.length(); i++) connected.add(connectedArray.optString(i));
        }

        JSONObject defaults = root.optJSONObject("default");
        if (defaults != null) {
            Iterator<String> keys = defaults.keys();
            while (keys.hasNext()) {
                String providerId = keys.next();
                providerDefaults.put(providerId, defaults.optString(providerId, ""));
            }
        }

        JSONArray all = root.optJSONArray("all");
        if (all == null) return;
        for (int i = 0; i < all.length(); i++) {
            JSONObject providerJson = all.optJSONObject(i);
            if (providerJson == null) continue;
            String providerId = providerJson.optString("id", "");
            if (providerId.isEmpty()) continue;
            ProviderChoice provider = new ProviderChoice(
                    providerId,
                    providerJson.optString("name", providerId),
                    connected.contains(providerId));

            JSONObject models = providerJson.optJSONObject("models");
            if (models != null) {
                Iterator<String> modelKeys = models.keys();
                while (modelKeys.hasNext()) {
                    String key = modelKeys.next();
                    JSONObject modelJson = models.optJSONObject(key);
                    if (modelJson == null) continue;
                    String id = modelJson.optString("id", key);
                    JSONObject caps = modelJson.optJSONObject("capabilities");
                    JSONObject limit = modelJson.optJSONObject("limit");
                    ModelChoice model = new ModelChoice(
                            id,
                            modelJson.optString("name", id),
                            modelJson.optString("status", ""),
                            caps != null && caps.optBoolean("reasoning", false),
                            limit == null ? 0L : limit.optLong("context", 0L));

                    JSONObject variants = modelJson.optJSONObject("variants");
                    if (variants != null) {
                        Iterator<String> variantKeys = variants.keys();
                        while (variantKeys.hasNext()) model.variants.add(variantKeys.next());
                        sortVariants(model.variants);
                    }
                    provider.models.add(model);
                }
            }
            providers.add(provider);
        }
    }

    private void reconcileAgent() {
        if (agents.isEmpty()) return;
        AgentChoice current = findAgent(selectedAgent);
        if (current != null) return;
        AgentChoice build = findAgent(DEFAULT_AGENT);
        selectedAgent = build != null ? build.name : agents.get(0).name;
        persistAgent();
    }

    private void reconcileModel() {
        ProviderChoice provider = findProvider(selectedProviderId);
        ModelChoice model = findModel(provider, selectedModelId);
        if (provider != null && provider.connected && model != null) {
            reconcileVariant(model);
            return;
        }

        AgentChoice agent = findAgent(selectedAgent);
        if (agent != null && !TextUtils.isEmpty(agent.providerId) && !TextUtils.isEmpty(agent.modelId)) {
            provider = findProvider(agent.providerId);
            model = findModel(provider, agent.modelId);
            if (provider != null && provider.connected && model != null) {
                applyModel(provider, model, false);
                if (!TextUtils.isEmpty(agent.variant) && model.variants.contains(agent.variant)) {
                    selectedVariant = agent.variant;
                }
                return;
            }
        }

        String recentProvider = prefs.getString("recentProviderId", null);
        String recentModel = prefs.getString("recentModelId", null);
        provider = findProvider(recentProvider);
        model = findModel(provider, recentModel);
        if (provider != null && provider.connected && model != null) {
            applyModel(provider, model, false);
            return;
        }

        for (ProviderChoice candidate : providers) {
            if (!candidate.connected) continue;
            String defaultId = providerDefaults.get(candidate.id);
            ModelChoice defaultModel = findModel(candidate, defaultId);
            if (defaultModel != null) {
                applyModel(candidate, defaultModel, false);
                return;
            }
        }

        for (ProviderChoice candidate : providers) {
            if (!candidate.connected || candidate.models.isEmpty()) continue;
            ArrayList<ModelChoice> models = new ArrayList<>(candidate.models);
            models.sort(Comparator.comparing(m -> m.name.toLowerCase(Locale.ROOT)));
            applyModel(candidate, models.get(0), false);
            return;
        }

        selectedProviderId = null;
        selectedModelId = null;
        selectedVariant = null;
    }

    private void applyModel(ProviderChoice provider, ModelChoice model, boolean persist) {
        selectedProviderId = provider.id;
        selectedModelId = model.id;
        selectedVariant = readVariantForCurrentModel();
        reconcileVariant(model);
        if (persist) {
            persistModelAndVariant();
            prefs.edit()
                    .putString("recentProviderId", provider.id)
                    .putString("recentModelId", model.id)
                    .apply();
        }
        updateLabels();
    }

    private void reconcileVariant(ModelChoice model) {
        if (selectedVariant != null && !model.variants.contains(selectedVariant)) selectedVariant = null;
    }

    private void restoreSelectionKeys() {
        selectedAgent = readScoped("agent", prefs.getString("selectedAgent", DEFAULT_AGENT));
        selectedProviderId = readScoped("provider", prefs.getString("selectedProviderId", null));
        selectedModelId = readScoped("model", prefs.getString("selectedModelId", null));
        selectedVariant = readVariantForCurrentModel();
    }

    private void persistAgent() {
        SharedPreferences.Editor edit = prefs.edit();
        edit.putString(scopedKey("agent"), selectedAgent);
        edit.putString("selectedAgent", selectedAgent);
        edit.apply();
    }

    private void persistModelAndVariant() {
        SharedPreferences.Editor edit = prefs.edit();
        if (selectedProviderId == null) {
            edit.remove(scopedKey("provider"));
            edit.remove(scopedKey("model"));
        } else {
            edit.putString(scopedKey("provider"), selectedProviderId);
            edit.putString(scopedKey("model"), selectedModelId);
            edit.putString("selectedProviderId", selectedProviderId);
            edit.putString("selectedModelId", selectedModelId);
        }
        edit.apply();
        persistVariant();
    }

    private void persistVariant() {
        String key = variantKey();
        if (key == null) return;
        SharedPreferences.Editor edit = prefs.edit();
        if (selectedVariant == null) edit.remove(key);
        else edit.putString(key, selectedVariant);
        edit.apply();
    }

    private String readVariantForCurrentModel() {
        String key = variantKey();
        if (key != null && prefs.contains(key)) return emptyToNull(prefs.getString(key, null));
        String legacy = prefs.getString("selectedVariant", "auto");
        if (legacy == null || "auto".equals(legacy)) return null;
        return legacy;
    }

    private String variantKey() {
        if (selectedProviderId == null || selectedModelId == null) return null;
        return scopedKey("variant." + selectedProviderId + "/" + selectedModelId);
    }

    private String readScoped(String suffix, String fallback) {
        String key = scopedKey(suffix);
        return prefs.contains(key) ? prefs.getString(key, fallback) : fallback;
    }

    private String scopedKey(String suffix) {
        return sessionId == null ? "composer." + suffix : "session." + sessionId + "." + suffix;
    }

    private void updateLabels() {
        AgentChoice agent = findAgent(selectedAgent);
        agentChip.setText(agent == null ? displayName(selectedAgent) : displayName(agent.name));

        ProviderChoice provider = findProvider(selectedProviderId);
        ModelChoice model = findModel(provider, selectedModelId);
        modelChip.setText(model == null ? "Select Model" : model.name);

        effortChip.setText(selectedVariant == null ? "Default" : displayName(selectedVariant));
    }

    private void showUsageSheet(JSONObject session, String messagesBody) {
        UsageSnapshot usage = computeUsage(messagesBody);
        ArrayList<OpenCodeSheet.Stat> stats = new ArrayList<>();
        stats.add(new OpenCodeSheet.Stat("Session", session.optString("title", sessionId)));
        stats.add(new OpenCodeSheet.Stat("Messages", formatInt(usage.all)));
        stats.add(new OpenCodeSheet.Stat("Provider", usage.providerLabel));
        stats.add(new OpenCodeSheet.Stat("Model", usage.modelLabel));
        stats.add(new OpenCodeSheet.Stat("Context limit", usage.limit > 0 ? formatLong(usage.limit) : "—"));
        stats.add(new OpenCodeSheet.Stat("Total tokens", usage.hasUsage ? formatLong(usage.total) : "—"));
        stats.add(new OpenCodeSheet.Stat("Usage", usage.hasUsage ? usage.usage + "%" : "—"));
        stats.add(new OpenCodeSheet.Stat("Input tokens", usage.hasUsage ? formatLong(usage.input) : "—"));
        stats.add(new OpenCodeSheet.Stat("Output tokens", usage.hasUsage ? formatLong(usage.output) : "—"));
        stats.add(new OpenCodeSheet.Stat("Reasoning tokens", usage.hasUsage ? formatLong(usage.reasoning) : "—"));
        stats.add(new OpenCodeSheet.Stat("Cache tokens", usage.hasUsage ? formatLong(usage.cacheRead) + " / " + formatLong(usage.cacheWrite) : "—"));
        stats.add(new OpenCodeSheet.Stat("User messages", formatInt(usage.user)));
        stats.add(new OpenCodeSheet.Stat("Assistant messages", formatInt(usage.assistant)));
        stats.add(new OpenCodeSheet.Stat("Total cost", formatCurrency(session.optDouble("cost", 0d))));
        JSONObject time = session.optJSONObject("time");
        stats.add(new OpenCodeSheet.Stat("Session created", formatTime(time == null ? 0L : time.optLong("created", 0L))));
        stats.add(new OpenCodeSheet.Stat("Last activity", formatTime(usage.lastActivity)));

        OpenCodeSheet.showStats(
                activity,
                usageView,
                "Session context",
                usage.hasUsage ? usage.usage + "% · " + formatLong(usage.total) + " tokens" : "No usage data yet",
                stats);
    }

    private UsageSnapshot computeUsage(String body) {
        UsageSnapshot result = new UsageSnapshot();
        try {
            JSONArray messages = new JSONArray(body == null ? "[]" : body);
            JSONObject lastAssistant = null;
            for (int i = 0; i < messages.length(); i++) {
                JSONObject item = messages.optJSONObject(i);
                if (item == null) continue;
                JSONObject info = item.optJSONObject("info");
                if (info == null) continue;
                String role = info.optString("role", "");
                result.all++;
                if ("user".equals(role)) result.user++;
                if ("assistant".equals(role)) {
                    result.assistant++;
                    JSONObject tokens = info.optJSONObject("tokens");
                    long total = tokenTotal(tokens);
                    if (total > 0) lastAssistant = info;
                }
            }

            if (lastAssistant == null) return result;
            JSONObject tokens = lastAssistant.optJSONObject("tokens");
            result.input = token(tokens, "input");
            result.output = token(tokens, "output");
            result.reasoning = token(tokens, "reasoning");
            JSONObject cache = tokens == null ? null : tokens.optJSONObject("cache");
            result.cacheRead = token(cache, "read");
            result.cacheWrite = token(cache, "write");
            result.total = result.input + result.output + result.reasoning + result.cacheRead + result.cacheWrite;
            result.providerId = lastAssistant.optString("providerID", "");
            result.modelId = lastAssistant.optString("modelID", "");
            JSONObject time = lastAssistant.optJSONObject("time");
            result.lastActivity = time == null ? 0L : time.optLong("created", 0L);

            ProviderChoice provider = findProvider(result.providerId);
            ModelChoice model = findModel(provider, result.modelId);
            result.providerLabel = provider == null ? emptyFallback(result.providerId, "—") : provider.name;
            result.modelLabel = model == null ? emptyFallback(result.modelId, "—") : model.name;
            result.limit = model == null ? 0L : model.contextLimit;
            result.usage = result.limit > 0 ? (int) Math.round((result.total * 100.0d) / result.limit) : 0;
            result.hasUsage = true;
        } catch (Exception ignored) {}
        return result;
    }

    private JSONObject findSession(String body, String id) {
        try {
            JSONArray sessions = new JSONArray(body);
            for (int i = 0; i < sessions.length(); i++) {
                JSONObject session = sessions.optJSONObject(i);
                if (session != null && id.equals(session.optString("id", ""))) return session;
            }
        } catch (Exception ignored) {}
        return null;
    }

    private AgentChoice findAgent(String name) {
        if (name == null) return null;
        for (AgentChoice agent : agents) if (name.equals(agent.name)) return agent;
        return null;
    }

    private ProviderChoice findProvider(String id) {
        if (id == null) return null;
        for (ProviderChoice provider : providers) if (id.equals(provider.id)) return provider;
        return null;
    }

    private ModelChoice findModel(ProviderChoice provider, String id) {
        if (provider == null || id == null) return null;
        for (ModelChoice model : provider.models) if (id.equals(model.id)) return model;
        return null;
    }

    private ModelChoice currentModel() {
        return findModel(findProvider(selectedProviderId), selectedModelId);
    }

    private static void sortVariants(List<String> variants) {
        final List<String> order = List.of("none", "minimal", "low", "medium", "high", "xhigh", "max", "thinking");
        Collections.sort(variants, (a, b) -> {
            int ia = order.indexOf(a);
            int ib = order.indexOf(b);
            if (ia < 0) ia = 100;
            if (ib < 0) ib = 100;
            if (ia != ib) return Integer.compare(ia, ib);
            return a.compareToIgnoreCase(b);
        });
    }

    private static String modelKey(String providerId, String modelId) {
        return (providerId == null ? "" : providerId) + "\u0001" + (modelId == null ? "" : modelId);
    }

    private static String[] splitModelKey(String key) {
        int split = key.indexOf('\u0001');
        if (split < 0) return new String[] {"", key};
        return new String[] {key.substring(0, split), key.substring(split + 1)};
    }

    private static String nullableString(JSONObject obj, String key) {
        if (obj == null || obj.isNull(key)) return "";
        return obj.optString(key, "");
    }

    private static String emptyToNull(String value) {
        return value == null || value.isEmpty() ? null : value;
    }

    private static String emptyFallback(String value, String fallback) {
        return value == null || value.isEmpty() ? fallback : value;
    }

    private static long token(JSONObject obj, String key) {
        return obj == null ? 0L : obj.optLong(key, 0L);
    }

    private static long tokenTotal(JSONObject tokens) {
        if (tokens == null) return 0L;
        JSONObject cache = tokens.optJSONObject("cache");
        return token(tokens, "input")
                + token(tokens, "output")
                + token(tokens, "reasoning")
                + token(cache, "read")
                + token(cache, "write");
    }

    private static String displayName(String value) {
        if (value == null || value.isEmpty()) return "Default";
        if ("xhigh".equals(value)) return "XHigh";
        String normalized = value.replace('-', ' ').replace('_', ' ');
        return normalized.substring(0, 1).toUpperCase(Locale.ROOT) + normalized.substring(1);
    }

    private static String formatLong(long value) {
        return NumberFormat.getIntegerInstance().format(value);
    }

    private static String formatInt(int value) {
        return NumberFormat.getIntegerInstance().format(value);
    }

    private static String formatCurrency(double value) {
        return NumberFormat.getCurrencyInstance(Locale.US).format(value);
    }

    private static String formatTime(long millis) {
        if (millis <= 0) return "—";
        return DateFormat.getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT).format(new Date(millis));
    }

    private void toast(String message) {
        Toast.makeText(activity, message, Toast.LENGTH_SHORT).show();
    }
}
