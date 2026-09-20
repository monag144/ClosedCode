package com.monag.speechduck;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Space;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String PREFS = "speech_duck";
    private SharedPreferences prefs;
    private Button monitorButton;
    private TextView statusText;
    private TextView percentText;
    private SeekBar duckSeek;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        buildUi();
        requestNotificationPermissionIfNeeded();
        refreshUi();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshUi();
    }

    private void buildUi() {
        int pad = dp(22);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, dp(28), pad, pad);
        root.setBackgroundColor(Color.rgb(247, 247, 247));

        TextView title = new TextView(this);
        title.setText("Speech Duck");
        title.setTextSize(30);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setTextColor(Color.rgb(20,20,20));
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Quiet Maps, YouTube, music and other media while you use speech-to-text.");
        subtitle.setTextSize(16);
        subtitle.setTextColor(Color.rgb(75,75,75));
        subtitle.setPadding(0, dp(6), 0, dp(22));
        root.addView(subtitle);

        statusText = new TextView(this);
        statusText.setTextSize(18);
        statusText.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        statusText.setPadding(dp(14), dp(14), dp(14), dp(14));
        root.addView(statusText, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        TextView levelLabel = new TextView(this);
        levelLabel.setText("Ducking level");
        levelLabel.setTextSize(18);
        levelLabel.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        levelLabel.setPadding(0, dp(28), 0, dp(4));
        root.addView(levelLabel);

        percentText = new TextView(this);
        percentText.setTextSize(15);
        percentText.setTextColor(Color.DKGRAY);
        root.addView(percentText);

        duckSeek = new SeekBar(this);
        duckSeek.setMax(50);
        duckSeek.setProgress(prefs.getInt("duck_percent", 10));
        duckSeek.setPadding(0, dp(8), 0, dp(8));
        duckSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                percentText.setText("During dictation: " + progress + "% of normal media volume");
                if (fromUser) {
                    prefs.edit().putInt("duck_percent", progress).apply();
                    notifySettingsChanged();
                }
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        root.addView(duckSeek, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));

        CheckBox anyMicCheck = new CheckBox(this);
        anyMicCheck.setText("Compatibility mode: duck for ANY active microphone recording");
        anyMicCheck.setTextSize(15);
        anyMicCheck.setChecked(prefs.getBoolean("any_mic", false));
        anyMicCheck.setPadding(0, dp(14), 0, dp(6));
        anyMicCheck.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean("any_mic", isChecked).apply();
            notifySettingsChanged();
        });
        root.addView(anyMicCheck);

        TextView compatibilityHelp = new TextView(this);
        compatibilityHelp.setText("Leave this off first. Turn it on only if your keyboard doesn't report voice typing as Android VOICE_RECOGNITION. It can also duck during voice recorders, camera recording, calls, or other mic use.");
        compatibilityHelp.setTextSize(13);
        compatibilityHelp.setTextColor(Color.rgb(90,90,90));
        root.addView(compatibilityHelp);

        Space spacer = new Space(this);
        root.addView(spacer, new LinearLayout.LayoutParams(1, dp(26)));

        monitorButton = new Button(this);
        monitorButton.setTextSize(17);
        monitorButton.setAllCaps(false);
        monitorButton.setOnClickListener(v -> toggleMonitoring());
        root.addView(monitorButton, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(54)));

        Button batteryButton = new Button(this);
        batteryButton.setText("Open battery settings");
        batteryButton.setAllCaps(false);
        batteryButton.setOnClickListener(v -> {
            try {
                Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                intent.setData(android.net.Uri.parse("package:" + getPackageName()));
                startActivity(intent);
            } catch (Exception ignored) {}
        });
        LinearLayout.LayoutParams batteryParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(50));
        batteryParams.topMargin = dp(10);
        root.addView(batteryButton, batteryParams);

        TextView note = new TextView(this);
        note.setText("Speech Duck does not capture microphone audio or read what you dictate. It only watches Android's recording-state metadata. While active, Android requires an ongoing foreground-service notification.");
        note.setTextSize(13);
        note.setTextColor(Color.rgb(85,85,85));
        note.setPadding(0, dp(22), 0, 0);
        root.addView(note);

        setContentView(root);
    }

    private void toggleMonitoring() {
        boolean enabled = prefs.getBoolean("enabled", false);
        if (enabled) {
            Intent stop = new Intent(this, SpeechDuckService.class);
            stop.setAction(SpeechDuckService.ACTION_STOP);
            startService(stop);
        } else {
            prefs.edit().putBoolean("enabled", true).apply();
            Intent start = new Intent(this, SpeechDuckService.class);
            start.setAction(SpeechDuckService.ACTION_START);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(start);
            else startService(start);
        }
        refreshUi();
    }

    private void notifySettingsChanged() {
        if (!prefs.getBoolean("enabled", false)) return;
        Intent intent = new Intent(this, SpeechDuckService.class);
        intent.setAction(SpeechDuckService.ACTION_SETTINGS_CHANGED);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent);
        else startService(intent);
    }

    private void refreshUi() {
        boolean enabled = prefs.getBoolean("enabled", false);
        int percent = prefs.getInt("duck_percent", 10);
        if (duckSeek != null && duckSeek.getProgress() != percent) duckSeek.setProgress(percent);
        if (percentText != null) percentText.setText("During dictation: " + percent + "% of normal media volume");
        if (monitorButton != null) monitorButton.setText(enabled ? "Stop monitoring" : "Start monitoring");
        if (statusText != null) {
            statusText.setText(enabled ? "● Monitoring is ON" : "○ Monitoring is OFF");
            statusText.setTextColor(enabled ? Color.rgb(20, 115, 55) : Color.rgb(120, 60, 60));
            statusText.setBackgroundColor(enabled ? Color.rgb(231, 247, 236) : Color.rgb(247, 235, 235));
        }
    }

    private void requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1001);
        }
    }

    private int dp(int value) {
        float density = getResources().getDisplayMetrics().density;
        return Math.round(value * density);
    }
}
