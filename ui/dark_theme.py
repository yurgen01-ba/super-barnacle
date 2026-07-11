from __future__ import annotations

import streamlit as st


DARK_THEME_CSS = """
<style>
:root {
    --pb-bg: #080a0f;
    --pb-bg-soft: #0d1118;
    --pb-panel: #11151d;
    --pb-panel-2: #161a22;
    --pb-border: #2a303a;
    --pb-border-soft: #1d232e;
    --pb-text: #e7eaf0;
    --pb-muted: #9aa3af;
    --pb-muted-2: #6f7785;
    --pb-primary: #2f7df6;
    --pb-primary-soft: #10264a;
    --pb-danger: #ff4d5f;
    --pb-success: #17c964;
    --pb-warning: #f5a524;
    --pb-radius: 16px;
    --pb-radius-sm: 10px;
    --pb-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

/* App base */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--pb-bg) !important;
    color: var(--pb-text) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background: var(--pb-bg-soft) !important;
    border-right: 1px solid var(--pb-border-soft) !important;
}

[data-testid="stSidebar"] * {
    color: var(--pb-text) !important;
}

/* Text */
p, span, label, div, h1, h2, h3, h4, h5, h6 {
    color: var(--pb-text);
}

small, .stCaptionContainer, [data-testid="stCaptionContainer"] {
    color: var(--pb-muted) !important;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius-sm) !important;
    box-shadow: none !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
    color: var(--pb-muted-2) !important;
}

/* Selectbox / Multiselect */
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"],
[data-baseweb="select"] {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border-radius: var(--pb-radius-sm) !important;
}

.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div,
[data-baseweb="select"] > div {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border-color: var(--pb-border) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul,
div[role="listbox"] {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    box-shadow: var(--pb-shadow) !important;
}

div[role="option"] {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
}

div[role="option"]:hover {
    background: var(--pb-primary-soft) !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
button[kind="secondary"],
button[kind="primary"] {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius-sm) !important;
    box-shadow: none !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--pb-primary-soft) !important;
    border-color: var(--pb-primary) !important;
    color: var(--pb-text) !important;
}

.stButton > button[kind="primary"],
button[kind="primary"] {
    background: var(--pb-primary-soft) !important;
    border-color: var(--pb-primary) !important;
}

/* Checkboxes / Radio */
.stCheckbox label,
.stRadio label {
    color: var(--pb-text) !important;
}

.stCheckbox [data-testid="stMarkdownContainer"] p,
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--pb-text) !important;
}

/* Sliders */
.stSlider [data-baseweb="slider"] {
    color: var(--pb-primary) !important;
}

.stSlider div[data-testid="stTickBar"] {
    background: transparent !important;
}

.stSlider [role="slider"] {
    background: var(--pb-danger) !important;
    border-color: var(--pb-danger) !important;
}

/* Progress */
.stProgress > div > div > div > div {
    background-color: var(--pb-primary) !important;
}

.stProgress > div > div {
    background-color: var(--pb-border) !important;
}

/* Expanders */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius-sm) !important;
}

[data-testid="stExpander"] details {
    background: var(--pb-panel) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius-sm) !important;
}

[data-testid="stExpander"] div[role="button"] p {
    color: var(--pb-text) !important;
}

/* File uploader */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] div {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
    border-color: var(--pb-border) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: var(--pb-panel-2) !important;
    border: 1px dashed var(--pb-border) !important;
    border-radius: var(--pb-radius) !important;
}

[data-testid="stFileUploaderDropzone"] * {
    color: var(--pb-text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--pb-border-soft) !important;
}

.stTabs [data-baseweb="tab"] {
    background: var(--pb-panel) !important;
    color: var(--pb-muted) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: 999px !important;
    margin-right: 8px !important;
}

.stTabs [aria-selected="true"] {
    background: var(--pb-primary-soft) !important;
    color: var(--pb-text) !important;
    border-color: var(--pb-primary) !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: var(--pb-primary-soft) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius) !important;
}

[data-testid="stAlert"] * {
    color: var(--pb-text) !important;
}

/* Dataframes / tables */
[data-testid="stTable"],
[data-testid="stDataFrame"] {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
}

/* Code / JSON */
.stCodeBlock,
pre,
code {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-border) !important;
    border-radius: var(--pb-radius-sm) !important;
}

/* Popovers / tooltips */
[data-testid="stPopover"],
[data-testid="stTooltipHoverTarget"] {
    color: var(--pb-text) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--pb-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--pb-border);
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--pb-muted-2);
}

/* Kill random white native BaseWeb surfaces */
div[class*="baseweb"],
div[class*="st-"],
section,
article {
    scrollbar-color: var(--pb-border) var(--pb-bg);
}

/* Keep white text readable on pills/badges */
code {
    color: #7ee787 !important;
}

/* Disabled widgets */
button:disabled,
input:disabled,
textarea:disabled,
[aria-disabled="true"] {
    background: #11141a !important;
    color: #5f6673 !important;
    border-color: #232936 !important;
    opacity: 1 !important;
}
</style>
"""


def apply_complete_dark_theme():
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
