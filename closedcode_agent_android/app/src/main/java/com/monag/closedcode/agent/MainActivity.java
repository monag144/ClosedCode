package com.monag.closedcode.agent;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final String PREFS = "closedcode_agent";
    private static final String KEY_TOKEN = "bridge_token";
    private static final String KEY_PORT = "bridge_port";
    private static final String KEY_PROVIDER = "provider";
    private static final String KEY_MODEL = "model";
    private static final int DEFAULT_PORT = 38765;

    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final String sessionId = "android-" + shortId();

    private EditText token;
    private EditText port;
    private EditText provider;
    private EditText model;
    private EditText mission;
    private TextView status;
    private TextView output;
    private TextView activity;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        int pad = Math.round(14 * getResources().getDisplayMetrics().density);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, pad, pad, pad);
        scroll.addView(root);

        root.addView(text("ClosedCode Agent", 24));
        root.addView(text("Android control plane → ClosedCode localhost bridge → Termux execution plane", 14));

        status = text("Bridge: NOT TESTED", 14);
        status.setPadding(0, pad, 0, pad / 2);
        root.addView(status);

        token = field("Pairing token", prefs.getString(KEY_TOKEN, ""), true);
        port = field("ClosedCode bridge port", String.valueOf(prefs.getInt(KEY_PORT, DEFAULT_PORT)), false);
        port.setInputType(InputType.TYPE_CLASS_NUMBER);
        provider = field("Provider", prefs.getString(KEY_PROVIDER, "nvidia"), false);
        model = field("Model", prefs.getString(KEY_MODEL, "nvidia/nemotron-3-super-120b-a12b"), false);
        root.addView(token);
        root.addView(port);
        root.addView(provider);
        root.addView(model);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        Button save = new Button(this);
        save.setText("Save");
        save.setOnClickListener(v -> save());
        Button ping = new Button(this);
        ping.setText("Test Bridge");
        ping.setOnClickListener(v -> ping());
        controls.addView(save);
        controls.addView(ping);
        root.addView(controls);

        root.addView(text("Mission / prompt", 16));
        mission = new EditText(this);
        mission.setHint("Enter a mission for the ClosedCode Termux agent");
        mission.setMinLines(4);
        mission.setGravity(Gravity.TOP);
        root.addView(mission, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        Button submit = new Button(this);
        submit.setText("Submit Mission");
        submit.setOnClickListener(v -> submit());
        root.addView(submit);

        root.addView(text("Session output", 16));
        output = text("No request submitted yet.", 13);
        output.setTextIsSelectable(true);
        root.addView(output);

        root.addView(text("Tool / command activity", 16));
        activity = text("session=" + sessionId, 13);
        activity.setTextIsSelectable(true);
        root.addView(activity);

        setContentView(scroll);
    }

    private static String shortId() {
        return UUID.randomUUID().toString().replace("-", "").substring(0, 12);
    }

    private TextView text(String value, int size) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(size);
        return v;
    }

    private EditText field(String hint, String value, boolean secret) {
        EditText v = new EditText(this);
        v.setHint(hint);
        v.setSingleLine(true);
        v.setText(value);
        if (secret) {
            v.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        }
        return v;
    }

    private Pairing pairing() {
        String t = token.getText().toString().trim();
        if (t.length() < 32) {
            Toast.makeText(this, "Pairing token must be at least 32 characters", Toast.LENGTH_SHORT).show();
            return null;
        }
        int p;
        try {
            p = Integer.parseInt(port.getText().toString().trim());
        } catch (NumberFormatException exc) {
            Toast.makeText(this, "Invalid port", Toast.LENGTH_SHORT).show();
            return null;
        }
        if (p < 1024 || p > 65535) {
            Toast.makeText(this, "Port must be 1024..65535", Toast.LENGTH_SHORT).show();
            return null;
        }
        return new Pairing(t, p);
    }

    private void save() {
        Pairing p = pairing();
        if (p == null) return;
        getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                .putString(KEY_TOKEN, p.token)
                .putInt(KEY_PORT, p.port)
                .putString(KEY_PROVIDER, provider.getText().toString().trim())
                .putString(KEY_MODEL, model.getText().toString().trim())
                .apply();
        Toast.makeText(this, "Settings saved locally", Toast.LENGTH_SHORT).show();
    }

    private void ping() {
        Pairing p = pairing();
        if (p == null) return;
        String id = "ping." + shortId();
        append("→ " + id + " system.ping");
        status.setText("Bridge: CHECKING");
        io.execute(() -> {
            try {
                JSONObject response = BridgeClient.ping(p.token, p.port, id, sessionId);
                runOnUiThread(() -> {
                    output.setText(response.toString());
                    append("✓ " + id + " " + response.optString("status", "ok"));
                    status.setText("Bridge: CONNECTED");
                });
            } catch (Exception exc) {
                runOnUiThread(() -> fail(id, exc));
            }
        });
    }

    private void submit() {
        Pairing p = pairing();
        if (p == null) return;
        String prompt = mission.getText().toString().trim();
        if (prompt.isEmpty()) {
            Toast.makeText(this, "Enter a mission", Toast.LENGTH_SHORT).show();
            return;
        }
        save();
        String id = "mission." + shortId();
        String providerValue = provider.getText().toString().trim();
        String modelValue = model.getText().toString().trim();
        append("→ " + id + " mission.submit RUNNING");
        append("  provider/model: " + providerValue + " / " + modelValue);
        output.setText("RUNNING\nrequest_id=" + id);
        long start = System.currentTimeMillis();

        io.execute(() -> {
            try {
                JSONObject response = BridgeClient.submitMission(
                        p.token,
                        p.port,
                        id,
                        sessionId,
                        prompt,
                        providerValue,
                        modelValue);
                long elapsed = System.currentTimeMillis() - start;
                runOnUiThread(() -> {
                    output.setText(response.toString());
                    append("✓ " + id + " " + response.optString("status", "ok") + " latency_ms=" + elapsed);
                    status.setText("Bridge: CONNECTED");
                });
            } catch (Exception exc) {
                long elapsed = System.currentTimeMillis() - start;
                runOnUiThread(() -> {
                    fail(id, exc);
                    append("  latency_ms=" + elapsed);
                });
            }
        });
    }

    private void fail(String id, Exception exc) {
        String message = exc.getMessage() == null ? "No message" : exc.getMessage();
        if (message.length() > 500) message = message.substring(0, 500);
        output.setText(exc.getClass().getSimpleName() + ": " + message);
        append("✗ " + id + " " + exc.getClass().getSimpleName());
        status.setText("Bridge: ERROR");
    }

    private void append(String line) {
        activity.setText(activity.getText().toString() + "\n" + line);
    }

    @Override
    protected void onDestroy() {
        io.shutdownNow();
        super.onDestroy();
    }

    private static final class Pairing {
        final String token;
        final int port;

        Pairing(String token, int port) {
            this.token = token;
            this.port = port;
        }
    }
}
