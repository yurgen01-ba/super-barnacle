from __future__ import annotations

import streamlit as st


COMPONENT_STYLES = """
<style>
.pb-card,
.pb-panel,
.pb-metric-card {
    background: linear-gradient(180deg, #171b23 0%, #10141b 100%);
    border: 1px solid #2a303a;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 20px 60px rgba(0,0,0,.25);
}

.pb-card-title,
.pb-panel-title,
.pb-metric-title {
    color: #e7eaf0;
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 8px;
}

.pb-card-body,
.pb-caption {
    color: #9aa3af;
    font-size: 14px;
    line-height: 1.5;
}

.pb-card-footer {
    color: #6f7785;
    font-size: 12px;
    margin-top: 14px;
}

.pb-metric-value {
    color: #e7eaf0;
    font-size: 34px;
    line-height: 1.15;
    margin-top: 8px;
}

.pb-metric-delta {
    display: inline-block;
    color: #d7fbe8;
    background: rgba(23, 201, 100, .13);
    border: 1px solid rgba(23, 201, 100, .20);
    border-radius: 999px;
    padding: 4px 9px;
    margin-top: 10px;
    font-size: 12px;
}

.pb-status-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 12px;
    border: 1px solid #2a303a;
    background: #161a22;
    color: #e7eaf0;
}

.pb-status-success {
    color: #d7fbe8;
    background: rgba(23, 201, 100, .13);
    border-color: rgba(23, 201, 100, .25);
}

.pb-status-warning {
    color: #fff2d2;
    background: rgba(245, 165, 36, .13);
    border-color: rgba(245, 165, 36, .25);
}

.pb-status-danger {
    color: #ffe4e8;
    background: rgba(255, 77, 95, .13);
    border-color: rgba(255, 77, 95, .25);
}

.pb-divider {
    height: 1px;
    background: #1d232e;
    margin: 22px 0;
}
</style>
"""


def apply_component_styles():
    st.markdown(COMPONENT_STYLES, unsafe_allow_html=True)
