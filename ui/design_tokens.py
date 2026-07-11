from __future__ import annotations

import streamlit as st


DESIGN_TOKENS_CSS = """
<style>
:root {
    --pb-color-bg: #080a0f;
    --pb-color-bg-soft: #0d1118;
    --pb-color-surface: #11151d;
    --pb-color-surface-2: #161a22;
    --pb-color-surface-3: #1b202a;

    --pb-color-border: #2a303a;
    --pb-color-border-soft: #1d232e;

    --pb-color-text: #e7eaf0;
    --pb-color-text-muted: #9aa3af;
    --pb-color-text-subtle: #6f7785;

    --pb-color-primary: #2f7df6;
    --pb-color-primary-soft: #10264a;

    --pb-color-danger: #ff4d5f;
    --pb-color-success: #17c964;
    --pb-color-warning: #f5a524;

    --pb-radius-xs: 8px;
    --pb-radius-sm: 10px;
    --pb-radius-md: 14px;
    --pb-radius-lg: 18px;
    --pb-radius-xl: 24px;
    --pb-radius-pill: 999px;

    --pb-space-1: 4px;
    --pb-space-2: 8px;
    --pb-space-3: 12px;
    --pb-space-4: 16px;
    --pb-space-5: 20px;
    --pb-space-6: 24px;

    --pb-shadow-card: 0 20px 60px rgba(0, 0, 0, .25);
    --pb-shadow-popover: 0 20px 80px rgba(0, 0, 0, .40);

    --pb-font-size-xs: 12px;
    --pb-font-size-sm: 14px;
    --pb-font-size-md: 16px;
    --pb-font-size-lg: 20px;
    --pb-font-size-xl: 28px;
}
</style>
"""


def apply_design_tokens():
    st.markdown(DESIGN_TOKENS_CSS, unsafe_allow_html=True)
