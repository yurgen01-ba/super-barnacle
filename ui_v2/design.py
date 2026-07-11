import streamlit as st


def inject_ui_v2_theme():
    st.markdown(
        """
        <style>
            :root {
                --pb-bg: #09090B;
                --pb-panel: #111318;
                --pb-panel-2: #18181B;
                --pb-border: #27272A;
                --pb-text: #FAFAFA;
                --pb-text-2: #D4D4D8;
                --pb-muted: #A1A1AA;
                --pb-blue: #3B82F6;
                --pb-green: #22C55E;
                --pb-yellow: #F59E0B;
            }

            .stApp {
                background: var(--pb-bg);
                color: var(--pb-text);
            }

            [data-testid="stHeader"] {
                display: none;
            }

            section[data-testid="stSidebar"] {
                display: none !important;
            }

            .block-container {
                padding: 1.25rem 1.4rem 2rem !important;
                max-width: 100% !important;
            }

            h1, h2, h3 {
                color: var(--pb-text);
                letter-spacing: -0.04em;
            }

            p, span, label {
                color: var(--pb-text-2);
            }

            div[data-testid="stMetric"] {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                padding: 1rem;
                background: linear-gradient(180deg, rgba(24,24,27,0.94), rgba(17,19,24,0.94));
            }

            div[data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: var(--pb-text);
            }

            div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
                color: var(--pb-green);
            }

            div[data-testid="stButton"] button {
                border-radius: 10px !important;
                border: 1px solid var(--pb-border) !important;
                background-color: rgba(24,24,27,0.92) !important;
                color: var(--pb-text) !important;
                box-shadow: none !important;
            }

            div[data-testid="stButton"] button:hover {
                border-color: rgba(59,130,246,0.55) !important;
                background-color: rgba(59,130,246,0.12) !important;
                color: #FFFFFF !important;
            }

            div[data-testid="stButton"] button[kind="primary"] {
                background-color: rgba(59,130,246,0.20) !important;
                border-color: rgba(59,130,246,0.65) !important;
                color: #FFFFFF !important;
            }

            div[data-testid="stButton"] button:disabled {
                background-color: rgba(24,24,27,0.38) !important;
                border-color: rgba(63,63,70,0.65) !important;
                color: rgba(161,161,170,0.48) !important;
                cursor: not-allowed !important;
            }

            div[data-testid="stTextArea"] textarea,
            div[data-testid="stTextInput"] input,
            div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                background: rgba(24,24,27,0.96) !important;
                border-color: var(--pb-border) !important;
                color: var(--pb-text) !important;
            }

            div[data-testid="stTabs"] button {
                border-radius: 999px !important;
                border: 1px solid var(--pb-border) !important;
                background: rgba(24,24,27,0.78) !important;
                color: var(--pb-muted) !important;
            }

            div[data-testid="stTabs"] button[aria-selected="true"] {
                color: white !important;
                border-color: rgba(59,130,246,0.65) !important;
                background: rgba(59,130,246,0.18) !important;
            }

            div[data-testid="stExpander"] {
                border: 1px solid var(--pb-border);
                border-radius: 14px;
                background: rgba(17,19,24,0.96);
                overflow: hidden;
                margin-bottom: 0.75rem;
            }

            div[data-testid="stFileUploader"] {
                border: 1px dashed #3F3F46;
                border-radius: 14px;
                background: rgba(24,24,27,0.55);
                padding: 0.75rem;
            }

            .pb-panel {
                border: 1px solid var(--pb-border);
                border-radius: 18px;
                background: linear-gradient(180deg, rgba(17,19,24,0.96), rgba(13,17,23,0.98));
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .pb-panel-title {
                font-weight: 800;
                color: var(--pb-text);
                font-size: 1.05rem;
                margin-bottom: 0.35rem;
            }

            .pb-caption {
                color: var(--pb-muted);
                font-size: 0.86rem;
                line-height: 1.45;
            }

            .pb-topbar {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                background: linear-gradient(180deg, rgba(17,19,24,0.96), rgba(13,17,23,0.96));
                padding: 0.9rem 1rem;
                margin-bottom: 1.3rem;
            }

            .pb-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
            }

            .pb-change-row {
                display: grid;
                grid-template-columns: 72px 1fr 90px;
                gap: 10px;
                align-items: center;
                padding: 0.72rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }

            .pb-change-row:last-child {
                border-bottom: none;
            }

            .pb-tag {
                display: inline-flex;
                justify-content: center;
                border: 1px solid var(--pb-border);
                border-radius: 8px;
                padding: 3px 8px;
                color: var(--pb-text-2);
                background: rgba(255,255,255,0.03);
                font-size: 0.75rem;
            }

            .pb-source-card {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                background: rgba(17,19,24,0.92);
                padding: 1rem;
                min-height: 108px;
            }

            .pb-source-title {
                color: white;
                font-weight: 720;
                margin-bottom: 0.3rem;
            }

            .pb-muted {
                color: var(--pb-muted);
            }

            .pb-yellow {
                color: var(--pb-yellow);
            }

            .pb-nonfunctional {
                color: var(--pb-muted);
                font-size: 0.78rem;
                opacity: 0.72;
                margin-top: 0.35rem;
            }

            .pb-chat-bubble {
                border: 1px solid var(--pb-border);
                border-radius: 14px;
                background: rgba(255,255,255,0.04);
                padding: 0.9rem;
                color: var(--pb-text-2);
                margin-bottom: 0.75rem;
                line-height: 1.5;
            }

            .pb-menu-block {
                border: 1px solid var(--pb-border);
                border-radius: 14px;
                background: rgba(17,19,24,0.86);
                padding: 0.75rem;
                margin-bottom: 0.85rem;
            }

            .pb-menu-block-title {
                color: var(--pb-text-2);
                font-weight: 700;
                font-size: 0.9rem;
                margin-bottom: 0.5rem;
            }

            .pb-submenu-item {
                color: var(--pb-muted);
                font-size: 0.86rem;
                padding: 0.28rem 0.1rem;
            }

            .pb-project-card {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                background: linear-gradient(180deg, rgba(17,19,24,0.96), rgba(13,17,23,0.98));
                padding: 0.9rem;
                margin-top: 0.75rem;
            }

            .pb-project-card-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.5rem;
            }

            .pb-project-label {
                color: var(--pb-muted);
                font-size: 0.78rem;
                margin-bottom: 0.25rem;
            }

            .pb-project-name {
                color: white;
                font-size: 1rem;
                font-weight: 800;
                letter-spacing: -0.02em;
            }

            .pb-small-button {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                border: 1px solid var(--pb-border);
                border-radius: 8px;
                background: rgba(255,255,255,0.03);
                color: var(--pb-muted);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
