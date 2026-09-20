package com.monag.speechduck;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.media.AudioManager;
import android.media.AudioRecordingConfiguration;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;

import java.util.List;

public class SpeechDuckService extends Service {
    public static final String ACTION_START = "com.monag.speechduck.START";
    public static final String ACTION_STOP = "com.monag.speechduck.STOP";
    public static final String ACTION_SETTINGS_CHANGED = "com.monag.speechduck.SETTINGS_CHANGED";

    private static final String PREFS = "speech_duck";
    private static final String CHANNEL_ID = "speech_duck_monitor";
    private static final int NOTIFICATION_ID = 7721;
    private static final long RESTORE_DELAY_MS = 350L;

    private AudioManager audioManager;
    private SharedPreferences prefs;
    private Handler mainHandler;
    private boolean callbackRegistered = false;
    private boolean ducked = false;
    private boolean recognitionActive = false;
    private int originalMusicVolume = -1;

    private final AudioManager.AudioRecordingCallback recordingCallback = new AudioManager.AudioRecordingCallback() {
        @Override
        public void onRecordingConfigChanged(List<AudioRecordingConfiguration> configs) {
            handleRecordingConfigs(configs);
        }
    };

    private final Runnable restoreRunnable = this::restoreVolumeNow;

    @Override
    public void onCreate() {
        super.onCreate();
        audioManager = (AudioManager) getSystemService(AUDIO_SERVICE);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        mainHandler = new Handler(Looper.getMainLooper());
        createNotificationChannel();
        recoverIfPreviousRunDiedWhileDucked();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? ACTION_START : intent.getAction();

        if (ACTION_STOP.equals(action)) {
            prefs.edit().putBoolean("enabled", false).apply();
            stopMonitoringAndRestore();
            stopForeground(STOP_FOREGROUND_REMOVE);
            stopSelf();
            return START_NOT_STICKY;
        }

        prefs.edit().putBoolean("enabled", true).apply();
        promoteToForeground();
        registerRecordingCallbackIfNeeded();
        handleRecordingConfigs(audioManager.getActiveRecordingConfigurations());
        return START_STICKY;
    }

    private void registerRecordingCallbackIfNeeded() {
        if (callbackRegistered) return;
        audioManager.registerAudioRecordingCallback(recordingCallback, mainHandler);
        callbackRegistered = true;
    }

    private void handleRecordingConfigs(List<AudioRecordingConfiguration> configs) {
        boolean anyMic = prefs.getBoolean("any_mic", false);
        boolean active = false;
        if (configs != null) {
            for (AudioRecordingConfiguration config : configs) {
                if (Build.VERSION.SDK_INT >= 29 && config.isClientSilenced()) continue;
                int source = config.getClientAudioSource();
                if (anyMic || source == MediaRecorder.AudioSource.VOICE_RECOGNITION) {
                    active = true;
                    break;
                }
            }
        }

        recognitionActive = active;
        if (active) {
            mainHandler.removeCallbacks(restoreRunnable);
            duckNow();
        } else if (ducked) {
            mainHandler.removeCallbacks(restoreRunnable);
            mainHandler.postDelayed(restoreRunnable, RESTORE_DELAY_MS);
        }
        updateNotification();
    }

    private void duckNow() {
        if (!ducked) {
            originalMusicVolume = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC);
            prefs.edit()
                    .putBoolean("duck_active", true)
                    .putInt("duck_original", originalMusicVolume)
                    .apply();
            ducked = true;
        }
        applyCurrentDuckLevel();
    }

    private void applyCurrentDuckLevel() {
        if (!ducked) return;
        int percent = clamp(prefs.getInt("duck_percent", 10), 0, 50);
        int max = audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
        int min = Build.VERSION.SDK_INT >= 28 ? audioManager.getStreamMinVolume(AudioManager.STREAM_MUSIC) : 0;
        int calculated = Math.round(max * (percent / 100f));
        if (percent == 0) calculated = min;
        int target = Math.max(min, Math.min(originalMusicVolume, calculated));
        try {
            audioManager.setStreamVolume(AudioManager.STREAM_MUSIC, target, 0);
        } catch (SecurityException ignored) {
        }
        updateNotification();
    }

    private void restoreVolumeNow() {
        if (recognitionActive || !ducked) return;
        try {
            if (originalMusicVolume >= 0) {
                audioManager.setStreamVolume(AudioManager.STREAM_MUSIC, originalMusicVolume, 0);
            }
        } catch (SecurityException ignored) {
        } finally {
            ducked = false;
            originalMusicVolume = -1;
            prefs.edit().putBoolean("duck_active", false).remove("duck_original").apply();
            updateNotification();
        }
    }

    private void recoverIfPreviousRunDiedWhileDucked() {
        if (!prefs.getBoolean("duck_active", false)) return;
        int oldVolume = prefs.getInt("duck_original", -1);
        if (oldVolume >= 0) {
            try {
                audioManager.setStreamVolume(AudioManager.STREAM_MUSIC, oldVolume, 0);
            } catch (SecurityException ignored) {}
        }
        prefs.edit().putBoolean("duck_active", false).remove("duck_original").apply();
    }

    private void stopMonitoringAndRestore() {
        mainHandler.removeCallbacks(restoreRunnable);
        recognitionActive = false;
        if (callbackRegistered) {
            audioManager.unregisterAudioRecordingCallback(recordingCallback);
            callbackRegistered = false;
        }
        if (ducked) restoreVolumeNow();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Speech Duck monitoring",
                    NotificationManager.IMPORTANCE_LOW);
            channel.setDescription("Keeps Speech Duck active so it can lower media volume during speech-to-text.");
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
    }

    private void promoteToForeground() {
        Notification notification = buildNotification();
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
    }

    private void updateNotification() {
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.notify(NOTIFICATION_ID, buildNotification());
    }

    private Notification buildNotification() {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent openPending = PendingIntent.getActivity(
                this, 0, openIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Intent stopIntent = new Intent(this, SpeechDuckService.class);
        stopIntent.setAction(ACTION_STOP);
        PendingIntent stopPending = PendingIntent.getService(
                this, 1, stopIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        String content;
        if (ducked && recognitionActive) {
            int percent = clamp(prefs.getInt("duck_percent", 10), 0, 50);
            content = "Speech-to-text active • media at " + percent + "%";
        } else {
            content = prefs.getBoolean("any_mic", false)
                    ? "Watching microphone activity"
                    : "Watching for speech-to-text";
        }

        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL_ID)
                : new Notification.Builder(this);

        return builder
                .setSmallIcon(com.monag.speechduck.R.drawable.ic_speechduck)
                .setContentTitle("Speech Duck is monitoring")
                .setContentText(content)
                .setContentIntent(openPending)
                .setOngoing(true)
                .setCategory(Notification.CATEGORY_SERVICE)
                .addAction(new Notification.Action.Builder(
                        android.R.drawable.ic_media_pause, "Stop", stopPending).build())
                .build();
    }

    @Override
    public void onDestroy() {
        stopMonitoringAndRestore();
        super.onDestroy();
    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        super.onTaskRemoved(rootIntent);
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }
}
