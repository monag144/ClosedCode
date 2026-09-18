package com.monag.closedcode.mobile;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;

public final class ContextUsageView extends View {
    private final Paint backgroundPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint progressPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF arc = new RectF();
    private int percentage;

    public ContextUsageView(Context context) {
        super(context);
        init();
    }

    public ContextUsageView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public ContextUsageView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        float stroke = dp(2);
        backgroundPaint.setStyle(Paint.Style.STROKE);
        backgroundPaint.setStrokeWidth(stroke);
        backgroundPaint.setStrokeCap(Paint.Cap.ROUND);
        backgroundPaint.setColor(getResources().getColor(R.color.cc_border, getContext().getTheme()));

        progressPaint.setStyle(Paint.Style.STROKE);
        progressPaint.setStrokeWidth(stroke);
        progressPaint.setStrokeCap(Paint.Cap.ROUND);
        progressPaint.setColor(getResources().getColor(R.color.cc_text, getContext().getTheme()));
        setContentDescription("Session context usage");
        setClickable(true);
        setFocusable(true);
    }

    public void setPercentage(int value) {
        percentage = Math.max(0, Math.min(100, value));
        setContentDescription("Session context usage " + percentage + "%");
        invalidate();
    }

    public int getPercentage() {
        return percentage;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float size = dp(16);
        float left = (getWidth() - size) / 2f;
        float top = (getHeight() - size) / 2f;
        float inset = dp(1);
        arc.set(left + inset, top + inset, left + size - inset, top + size - inset);
        canvas.drawArc(arc, 0f, 360f, false, backgroundPaint);
        if (percentage > 0) {
            canvas.drawArc(arc, -90f, 360f * (percentage / 100f), false, progressPaint);
        }
    }

    private float dp(float value) {
        return value * getResources().getDisplayMetrics().density;
    }
}
