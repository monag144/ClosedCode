package com.monag.closedcode.mobile;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.view.animation.DecelerateInterpolator;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class OpenCodeSheet {
    public static final long TRANSITION_MS = 120L;

    public static final class Choice {
        public final String id;
        public final String title;
        public final String subtitle;
        public final String section;

        public Choice(String id, String title, String subtitle, String section) {
            this.id = id == null ? "" : id;
            this.title = title == null ? "" : title;
            this.subtitle = subtitle == null ? "" : subtitle;
            this.section = section == null ? "" : section;
        }
    }

    public static final class Stat {
        public final String label;
        public final String value;

        public Stat(String label, String value) {
            this.label = label == null ? "" : label;
            this.value = value == null ? "—" : value;
        }
    }

    public interface ChoiceListener {
        void selected(Choice choice);
    }

    private OpenCodeSheet() {}

    public static void showChoices(
            Activity activity,
            View trigger,
            String title,
            String subtitle,
            List<Choice> choices,
            String selectedId,
            ChoiceListener listener) {
        Dialog dialog = new Dialog(activity);
        LinearLayout root = baseRoot(activity, title, subtitle);
        ScrollView scroll = new ScrollView(activity);
        scroll.setFillViewport(false);
        LinearLayout list = new LinearLayout(activity);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setPadding(dp(activity, 12), 0, dp(activity, 12), dp(activity, 18));
        scroll.addView(list, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f));

        appendChoices(activity, dialog, root, list, trigger, choices, selectedId, listener);
        present(activity, dialog, root, trigger, 0.58f, null);
    }

    public static void showSearchChoices(
            Activity activity,
            View trigger,
            String title,
            String subtitle,
            List<Choice> choices,
            String selectedId,
            ChoiceListener listener) {
        Dialog dialog = new Dialog(activity);
        LinearLayout root = baseRoot(activity, title, subtitle);

        EditText search = new EditText(activity);
        search.setSingleLine(true);
        search.setHint("Search models…");
        search.setTextColor(activity.getColor(R.color.cc_text));
        search.setHintTextColor(activity.getColor(R.color.cc_muted));
        search.setTextSize(15);
        search.setPadding(dp(activity, 14), dp(activity, 8), dp(activity, 14), dp(activity, 8));
        search.setBackground(roundRect(activity, activity.getColor(R.color.cc_surface_2), 14, activity.getColor(R.color.cc_border), 1));
        LinearLayout.LayoutParams searchLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(activity, 46));
        searchLp.setMargins(dp(activity, 12), dp(activity, 6), dp(activity, 12), dp(activity, 10));
        root.addView(search, searchLp);

        ScrollView scroll = new ScrollView(activity);
        LinearLayout list = new LinearLayout(activity);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setPadding(dp(activity, 12), 0, dp(activity, 12), dp(activity, 18));
        scroll.addView(list, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f));

        Runnable rebuild = () -> {
            String query = search.getText().toString().trim().toLowerCase(Locale.ROOT);
            ArrayList<Choice> filtered = new ArrayList<>();
            for (Choice choice : choices) {
                String haystack = (choice.title + "\n" + choice.subtitle + "\n" + choice.section).toLowerCase(Locale.ROOT);
                if (query.isEmpty() || haystack.contains(query)) filtered.add(choice);
            }
            list.removeAllViews();
            appendChoices(activity, dialog, root, list, trigger, filtered, selectedId, listener);
            if (filtered.isEmpty()) {
                TextView empty = text(activity, "No matching models", 13, R.color.cc_muted);
                empty.setGravity(Gravity.CENTER);
                empty.setPadding(0, dp(activity, 30), 0, dp(activity, 30));
                list.addView(empty);
            }
        };
        rebuild.run();

        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { rebuild.run(); }
            @Override public void afterTextChanged(Editable s) {}
        });

        present(activity, dialog, root, trigger, 0.82f, search);
    }

    public static void showStats(
            Activity activity,
            View trigger,
            String title,
            String subtitle,
            List<Stat> stats) {
        Dialog dialog = new Dialog(activity);
        LinearLayout root = baseRoot(activity, title, subtitle);
        ScrollView scroll = new ScrollView(activity);
        LinearLayout list = new LinearLayout(activity);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setPadding(dp(activity, 18), dp(activity, 4), dp(activity, 18), dp(activity, 24));

        for (Stat stat : stats) {
            LinearLayout row = new LinearLayout(activity);
            row.setOrientation(LinearLayout.VERTICAL);
            row.setPadding(0, dp(activity, 8), 0, dp(activity, 8));
            TextView label = text(activity, stat.label, 12, R.color.cc_muted);
            TextView value = text(activity, stat.value, 13, R.color.cc_text);
            value.setTypeface(null, Typeface.BOLD);
            value.setPadding(0, dp(activity, 3), 0, 0);
            value.setTextIsSelectable(true);
            row.addView(label);
            row.addView(value);
            list.addView(row);
        }

        scroll.addView(list, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f));
        present(activity, dialog, root, trigger, 0.78f, null);
    }

    private static LinearLayout baseRoot(Activity activity, String title, String subtitle) {
        LinearLayout root = new LinearLayout(activity);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(0, dp(activity, 8), 0, 0);
        root.setBackground(roundRect(activity, activity.getColor(R.color.cc_surface), 24, activity.getColor(R.color.cc_border), 1));

        View handle = new View(activity);
        GradientDrawable handleBg = new GradientDrawable();
        handleBg.setColor(activity.getColor(R.color.cc_border));
        handleBg.setCornerRadius(dp(activity, 99));
        handle.setBackground(handleBg);
        handle.setClickable(true);
        handle.setFocusable(true);
        handle.setContentDescription("Drag sheet up to expand or down to close");
        LinearLayout.LayoutParams handleLp = new LinearLayout.LayoutParams(dp(activity, 42), dp(activity, 4));
        handleLp.gravity = Gravity.CENTER_HORIZONTAL;
        handleLp.setMargins(0, dp(activity, 2), 0, dp(activity, 12));
        root.addView(handle, handleLp);

        TextView heading = text(activity, title, 18, R.color.cc_text);
        heading.setTypeface(null, Typeface.BOLD);
        heading.setPadding(dp(activity, 18), 0, dp(activity, 18), 0);
        root.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        if (subtitle != null && !subtitle.trim().isEmpty()) {
            TextView sub = text(activity, subtitle, 12, R.color.cc_muted);
            sub.setPadding(dp(activity, 18), dp(activity, 5), dp(activity, 18), dp(activity, 8));
            root.addView(sub, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT));
        } else {
            View spacer = new View(activity);
            root.addView(spacer, new LinearLayout.LayoutParams(1, dp(activity, 10)));
        }
        return root;
    }

    private static void appendChoices(
            Activity activity,
            Dialog dialog,
            View content,
            LinearLayout list,
            View trigger,
            List<Choice> choices,
            String selectedId,
            ChoiceListener listener) {
        String section = null;
        for (Choice choice : choices) {
            if (!choice.section.equals(section)) {
                section = choice.section;
                if (!section.isEmpty()) {
                    TextView header = text(activity, section.toUpperCase(Locale.ROOT), 10, R.color.cc_muted);
                    header.setTypeface(null, Typeface.BOLD);
                    header.setPadding(dp(activity, 8), dp(activity, 12), dp(activity, 8), dp(activity, 6));
                    list.addView(header);
                }
            }

            boolean selected = choice.id.equals(selectedId);
            LinearLayout row = new LinearLayout(activity);
            row.setOrientation(LinearLayout.VERTICAL);
            row.setPadding(dp(activity, 12), dp(activity, 10), dp(activity, 12), dp(activity, 10));
            row.setClickable(true);
            row.setFocusable(true);
            row.setBackground(roundRect(
                    activity,
                    selected ? activity.getColor(R.color.cc_surface_2) : Color.TRANSPARENT,
                    12,
                    selected ? activity.getColor(R.color.cc_border) : Color.TRANSPARENT,
                    selected ? 1 : 0));

            LinearLayout top = new LinearLayout(activity);
            top.setOrientation(LinearLayout.HORIZONTAL);
            top.setGravity(Gravity.CENTER_VERTICAL);
            TextView label = text(activity, choice.title, 14, selected ? R.color.cc_accent : R.color.cc_text);
            label.setTypeface(null, selected ? Typeface.BOLD : Typeface.NORMAL);
            top.addView(label, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
            if (selected) {
                TextView check = text(activity, "✓", 16, R.color.cc_accent);
                check.setGravity(Gravity.END);
                top.addView(check, new LinearLayout.LayoutParams(dp(activity, 28), ViewGroup.LayoutParams.WRAP_CONTENT));
            }
            row.addView(top);

            if (!choice.subtitle.isEmpty()) {
                TextView sub = text(activity, choice.subtitle, 11, R.color.cc_muted);
                sub.setPadding(0, dp(activity, 3), 0, 0);
                row.addView(sub);
            }

            row.setOnClickListener(v -> dismissThen(dialog, content, trigger, () -> listener.selected(choice)));
            LinearLayout.LayoutParams rowLp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT);
            rowLp.setMargins(0, dp(activity, 2), 0, dp(activity, 2));
            list.addView(row, rowLp);
        }
    }

    private static void present(
            Activity activity,
            Dialog dialog,
            View content,
            View trigger,
            float heightFraction,
            EditText focus) {
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        dialog.setContentView(content);

        Window window = dialog.getWindow();
        if (window == null) return;
        window.setBackgroundDrawableResource(android.R.color.transparent);
        window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        WindowManager.LayoutParams attrs = window.getAttributes();
        attrs.gravity = Gravity.BOTTOM;
        attrs.width = WindowManager.LayoutParams.MATCH_PARENT;
        attrs.height = Math.max(dp(activity, 260), (int) (activity.getResources().getDisplayMetrics().heightPixels * heightFraction));
        attrs.dimAmount = 0.52f;
        window.setAttributes(attrs);

        dialog.setOnDismissListener(d -> {
            if (trigger != null) {
                trigger.animate().cancel();
                trigger.setAlpha(1f);
                trigger.setScaleX(1f);
                trigger.setScaleY(1f);
            }
        });

        dialog.setOnShowListener(d -> {
            if (trigger != null) trigger.animate().alpha(0.64f).setDuration(TRANSITION_MS).start();
            content.setAlpha(0f);
            content.setScaleX(0.96f);
            content.setScaleY(0.96f);
            content.setPivotX(content.getWidth() / 2f);
            content.setPivotY(content.getHeight());
            content.animate()
                    .alpha(1f)
                    .scaleX(1f)
                    .scaleY(1f)
                    .setDuration(TRANSITION_MS)
                    .setInterpolator(new DecelerateInterpolator())
                    .start();
            if (focus != null) {
                new Handler(Looper.getMainLooper()).postDelayed(() -> {
                    focus.requestFocus();
                    InputMethodManager imm = (InputMethodManager) activity.getSystemService(Context.INPUT_METHOD_SERVICE);
                    if (imm != null) imm.showSoftInput(focus, InputMethodManager.SHOW_IMPLICIT);
                }, TRANSITION_MS);
            }
        });

        if (focus != null) {
            window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        }
        attachSheetDrag(activity, dialog, content, window, heightFraction);
        dialog.show();
    }

    private static void attachSheetDrag(
            Activity activity,
            Dialog dialog,
            View content,
            Window window,
            float initialHeightFraction) {
        if (!(content instanceof ViewGroup)) return;
        ViewGroup group = (ViewGroup) content;
        if (group.getChildCount() == 0) return;
        View handle = group.getChildAt(0);
        final float[] startRawY = {0f};
        final boolean[] moved = {false};
        final int touchSlop = dp(activity, 6);
        final int dismissFloor = dp(activity, 120);

        handle.setOnTouchListener((v, event) -> {
            if (!dialog.isShowing() && event.getActionMasked() != MotionEvent.ACTION_DOWN) return false;
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    content.animate().cancel();
                    startRawY[0] = event.getRawY();
                    moved[0] = false;
                    v.getParent().requestDisallowInterceptTouchEvent(true);
                    return true;
                case MotionEvent.ACTION_MOVE:
                    float dy = event.getRawY() - startRawY[0];
                    if (Math.abs(dy) >= touchSlop) moved[0] = true;
                    if (moved[0]) {
                        float upwardLimit = -dp(activity, 72);
                        content.setTranslationY(Math.max(upwardLimit, dy));
                    }
                    return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    v.getParent().requestDisallowInterceptTouchEvent(false);
                    float releaseDy = event.getRawY() - startRawY[0];
                    if (event.getActionMasked() == MotionEvent.ACTION_CANCEL || !moved[0]) {
                        content.animate().translationY(0f).setDuration(TRANSITION_MS).setInterpolator(new DecelerateInterpolator()).start();
                        return true;
                    }
                    int contentHeight = Math.max(1, content.getHeight());
                    int dismissThreshold = Math.max(dismissFloor, Math.round(contentHeight * 0.22f));
                    if (releaseDy >= dismissThreshold) {
                        content.animate()
                                .translationY(contentHeight)
                                .alpha(0.35f)
                                .setDuration(TRANSITION_MS)
                                .setInterpolator(new DecelerateInterpolator())
                                .withEndAction(dialog::dismiss)
                                .start();
                        return true;
                    }
                    if (releaseDy <= -dp(activity, 48)) {
                        WindowManager.LayoutParams expanded = window.getAttributes();
                        int target = (int) (activity.getResources().getDisplayMetrics().heightPixels * 0.94f);
                        expanded.height = Math.max(expanded.height, target);
                        window.setAttributes(expanded);
                        content.animate().translationY(0f).alpha(1f).setDuration(TRANSITION_MS).setInterpolator(new DecelerateInterpolator()).start();
                        return true;
                    }
                    content.animate().translationY(0f).alpha(1f).setDuration(TRANSITION_MS).setInterpolator(new DecelerateInterpolator()).start();
                    return true;
                default:
                    return false;
            }
        });
    }

    private static void dismissThen(Dialog dialog, View content, View trigger, Runnable after) {
        if (!dialog.isShowing()) return;
        if (trigger != null) trigger.animate().alpha(1f).setDuration(TRANSITION_MS).start();
        content.animate()
                .alpha(0f)
                .scaleX(0.96f)
                .scaleY(0.96f)
                .setDuration(TRANSITION_MS)
                .setInterpolator(new DecelerateInterpolator())
                .withEndAction(() -> {
                    dialog.dismiss();
                    after.run();
                })
                .start();
    }

    private static TextView text(Activity activity, String value, float sp, int colorRes) {
        TextView view = new TextView(activity);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(activity.getColor(colorRes));
        return view;
    }

    private static GradientDrawable roundRect(Activity activity, int fill, int radiusDp, int stroke, int strokeDp) {
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(fill);
        bg.setCornerRadius(dp(activity, radiusDp));
        if (strokeDp > 0 && Color.alpha(stroke) > 0) bg.setStroke(dp(activity, strokeDp), stroke);
        return bg;
    }

    private static int dp(Activity activity, int value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
