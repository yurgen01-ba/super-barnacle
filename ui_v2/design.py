import streamlit as st
from ui_v2.assets import logo_data_uri, svg_data_uri


def inject_ui_v2_theme(theme: str = "dark"):
    light = theme == "light"
    logo = logo_data_uri()
    google_icon = svg_data_uri("google")
    facebook_icon = svg_data_uri("facebook")
    slack_icon = svg_data_uri("slack")
    jira_icon = svg_data_uri("jira")
    confluence_icon = svg_data_uri("confluence")
    light_overrides = """
        .st-key-pb_navigation div[data-testid="stButton"] button,
        .st-key-pb_navigation div[data-testid="stButton"] button p,
        .st-key-pb_navigation div[data-testid="stButton"] button span {
            color: #343840 !important;
        }
        .st-key-pb_navigation div[data-testid="stButton"] button[kind="primary"],
        .st-key-pb_navigation div[data-testid="stButton"] button[kind="primary"] p {
            color: #15171A !important;
            background: #E5E9EF !important;
        }
        div[data-testid="stButton"] button:not([kind="primary"]),
        div[data-testid="stButton"] button:not([kind="primary"]) p,
        [data-testid="stFormSubmitButton"] button:not([kind*="primary"]),
        [data-testid="stFormSubmitButton"] button:not([kind*="primary"]) p {
            background: #FFFFFF !important;
            color: #343840 !important;
            -webkit-text-fill-color: #343840 !important;
            border-color: #D6DAE1 !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stSelectbox"] [role="group"],
        div[data-testid="stSelectbox"] input[role="combobox"],
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #FFFFFF !important;
            color: #15171A !important;
            -webkit-text-fill-color: #15171A !important;
            border-color: #D6DAE1 !important;
        }
        div[data-testid="stSelectbox"] *,
        .st-key-pb_topbar div[data-testid="stButton"] button * {
            color: #15171A !important;
            -webkit-text-fill-color: #15171A !important;
        }
        div[data-testid="stExpander"],
        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] summary,
        .st-key-pb_topbar,
        .pb-panel,
        .pb-source-card,
        .pb-chat-bubble {
            background: #FFFFFF !important;
            color: #15171A !important;
            border-color: #D6DAE1 !important;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            color: #15171A !important;
            border-color: #D6DAE1 !important;
        }
        div[data-testid="stMetric"] * {
            color: #15171A !important;
            -webkit-text-fill-color: #15171A !important;
        }
        h1, h2, h3, p, span, label,
        .pb-brand-title, .pb-source-title, .pb-project-name {
            color: #15171A !important;
        }
    """ if light else ""
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
                --pb-red: #FF4B4B;
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

            div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
                display: none !important;
            }

            div[data-testid="stButton"] button {
                border-radius: 10px !important;
                border: 1px solid var(--pb-border) !important;
                background-color: rgba(24,24,27,0.92) !important;
                color: var(--pb-text) !important;
                box-shadow: none !important;
            }

            [data-testid="stFormSubmitButton"] button,
            [data-testid="stDownloadButton"] button,
            button[data-testid^="stBaseButton"] {
                border-radius: 10px !important;
                border: 1px solid var(--pb-border) !important;
                background: #18181B !important;
                color: #E4E4E7 !important;
                -webkit-text-fill-color: #E4E4E7 !important;
                box-shadow: none !important;
            }

            [data-testid="stFormSubmitButton"] button *,
            [data-testid="stDownloadButton"] button *,
            button[data-testid^="stBaseButton"] * {
                color: inherit !important;
                -webkit-text-fill-color: inherit !important;
            }

            [data-testid="stFormSubmitButton"] button:hover,
            [data-testid="stDownloadButton"] button:hover,
            button[data-testid^="stBaseButton"]:hover {
                border-color: rgba(59,130,246,0.55) !important;
                background: rgba(59,130,246,0.12) !important;
                color: #FFFFFF !important;
            }

            [data-testid="stFormSubmitButton"] button:disabled,
            [data-testid="stDownloadButton"] button:disabled,
            button[data-testid^="stBaseButton"]:disabled {
                border-color: rgba(63,63,70,0.72) !important;
                background: rgba(24,24,27,0.58) !important;
                color: #71717A !important;
                -webkit-text-fill-color: #71717A !important;
                opacity: 1 !important;
            }

            div[data-testid="stButton"] button:hover {
                border-color: rgba(59,130,246,0.55) !important;
                background-color: rgba(59,130,246,0.12) !important;
                color: #FFFFFF !important;
            }

            div[data-testid="stButton"] button[kind="primary"] {
                background-color: var(--pb-red) !important;
                border-color: var(--pb-red) !important;
                color: #FFFFFF !important;
            }

            [data-testid="stFormSubmitButton"] button[kind*="primary"] {
                background: var(--pb-red) !important;
                border-color: var(--pb-red) !important;
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }

            div[data-testid="stButton"] button[kind="primary"]:hover,
            [data-testid="stFormSubmitButton"] button[kind*="primary"]:hover {
                background: #FF6262 !important;
                border-color: #FF7777 !important;
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
            div[data-testid="stSelectbox"] div[data-baseweb="select"],
            div[data-testid="stSelectbox"] [role="group"],
            div[data-testid="stSelectbox"] input[role="combobox"] {
                background: rgba(24,24,27,0.96) !important;
                border-color: var(--pb-border) !important;
                color: var(--pb-text) !important;
            }

            div[data-testid="stTextArea"] textarea::placeholder,
            div[data-testid="stTextInput"] input::placeholder {
                color: #A1A1AA !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #A1A1AA !important;
            }

            div[data-testid="stSelectbox"] button,
            div[data-testid="stSelectbox"] svg {
                color: #D4D4D8 !important;
                fill: #D4D4D8 !important;
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

            div[data-testid="stExpander"] details,
            div[data-testid="stExpander"] summary,
            details[data-testid="stExpander"] > summary {
                background: #111318 !important;
                color: var(--pb-text-2) !important;
            }

            div[data-testid="stExpander"] summary:hover {
                background: #18181B !important;
                color: #FFFFFF !important;
            }

            div[data-testid="stFileUploader"] {
                border: 1px dashed #3F3F46;
                border-radius: 14px;
                background: rgba(24,24,27,0.55);
                padding: 0.75rem;
            }

            [data-testid="stFileUploaderDropzone"],
            [data-testid="stFileUploaderDropzone"] > div,
            div[data-testid="stFileUploader"] section {
                background: #18181B !important;
                color: var(--pb-text-2) !important;
                border-color: #3F3F46 !important;
            }

            [data-testid="stFileUploaderDropzone"] button,
            [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {
                background: #27272A !important;
                border: 1px solid #3F3F46 !important;
                color: #E4E4E7 !important;
            }

            [data-testid="stFileUploaderDropzone"] button *,
            [data-testid="stFileUploaderDropzoneInstructions"],
            [data-testid="stFileUploaderDropzoneInstructions"] * {
                color: #D4D4D8 !important;
                -webkit-text-fill-color: #D4D4D8 !important;
            }

            div[data-testid="stJson"],
            div[data-testid="stJson"] > div,
            div[data-testid="stJson"] pre,
            div[data-testid="stJson"] .react-json-view {
                background: #111318 !important;
                color: #D4D4D8 !important;
            }

            div[data-baseweb="popover"],
            div[data-baseweb="menu"],
            [data-testid="stSelectboxVirtualDropdown"],
            [role="listbox"] {
                background: #18181B !important;
                color: var(--pb-text) !important;
                border-color: #3F3F46 !important;
            }

            [role="option"],
            [role="option"] > div {
                background: #18181B !important;
                color: #E4E4E7 !important;
                -webkit-text-fill-color: #E4E4E7 !important;
            }

            [role="option"][data-focused="true"],
            [role="option"][aria-selected="true"],
            [role="option"]:hover,
            [role="option"][data-focused="true"] > div,
            [role="option"][aria-selected="true"] > div,
            [role="option"]:hover > div {
                background: #27272A !important;
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }

            [data-testid="stCheckbox"] label:not([data-selected="true"]) > div:first-of-type {
                background: #18181B !important;
                border: 1px solid #52525B !important;
            }

            [data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type {
                border-color: #FF4B4B !important;
            }

            [data-testid="stRadioOption"]:not([data-selected="true"]) > div > div > div:first-child {
                background: #18181B !important;
                border: 1px solid #52525B !important;
            }

            [data-testid="stRadioOption"]:not([data-selected="true"]) > div > div > div:first-child > div {
                background: #18181B !important;
            }

            [role="tooltip"],
            [data-testid="stTooltipContent"] {
                background: #18181B !important;
                color: #E4E4E7 !important;
                border: 1px solid #3F3F46 !important;
                box-shadow: 0 10px 28px rgba(0,0,0,0.42) !important;
            }

            [data-testid="stTooltipContent"] *,
            [role="tooltip"] * {
                color: #E4E4E7 !important;
                -webkit-text-fill-color: #E4E4E7 !important;
            }

            .st-key-pb_navigation {
                margin-top: 0.75rem;
            }

            .st-key-pb_navigation [data-testid="stCaptionContainer"] {
                margin: 1.15rem 0 0.35rem;
                letter-spacing: 0.08em;
                font-size: 0.68rem;
            }

            .st-key-pb_navigation div[data-testid="stButton"] {
                margin: 0.05rem 0 !important;
            }

            .st-key-pb_navigation div[data-testid="stButton"] button {
                justify-content: flex-start !important;
                text-align: left !important;
                min-height: 2.35rem !important;
                padding: 0.48rem 0.7rem !important;
                border: 0 !important;
                border-left: 2px solid transparent !important;
                border-radius: 7px !important;
                background: transparent !important;
                color: #B8B8C0 !important;
                font-weight: 500 !important;
                font-size: 0.82rem !important;
                white-space: nowrap !important;
            }

            .st-key-pb_navigation div[data-testid="stButton"] button > div,
            .st-key-pb_navigation div[data-testid="stButton"] button span,
            .st-key-pb_navigation div[data-testid="stButton"] button p {
                width: 100% !important;
                justify-content: flex-start !important;
                text-align: left !important;
            }

            .st-key-pb_navigation div[data-testid="stButton"] button:hover {
                background: rgba(255,255,255,0.055) !important;
                color: #FFFFFF !important;
            }

            .st-key-pb_navigation div[data-testid="stButton"] button[kind="primary"] {
                border-left-color: #D4D4D8 !important;
                background: rgba(255,255,255,0.075) !important;
                color: #FFFFFF !important;
            }

            .pb-brand {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                padding: 0.55rem 0.45rem 0.8rem;
                border-bottom: 1px solid var(--pb-border);
            }

            .pb-auth-heading {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.35rem;
                padding: 3rem 0 1.25rem;
                text-align: center;
            }

            .pb-auth-heading h1,
            .pb-auth-heading p {
                margin: 0;
            }

            .pb-auth-separator {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin: 1rem 0;
                color: var(--pb-muted);
            }

            .pb-auth-separator::before,
            .pb-auth-separator::after {
                content: "";
                height: 1px;
                flex: 1;
                background: var(--pb-border);
            }

            .pb-brand-mark {
                display: flex;
                width: 30px;
                height: 30px;
                align-items: center;
                justify-content: center;
                border: 1px solid #71717A;
                border-radius: 7px;
                color: #F4F4F5;
                font-size: 0.72rem;
                font-weight: 800;
            }

            .pb-brand-title {
                color: #FAFAFA;
                font-weight: 750;
            }

            .pb-current-project {
                margin-top: 1.1rem;
                padding: 0.75rem 0.7rem;
                border-top: 1px solid var(--pb-border);
            }

            .pb-topbar-project {
                margin-left: 0.6rem;
                color: #FFFFFF;
                font-weight: 700;
            }

            .pb-knowledge-indicator {
                display: flex;
                align-items: center;
                gap: 0.65rem;
            }

            .pb-knowledge-value {
                color: #F4F4F5;
                border: 1px solid #52525B;
                border-radius: 999px;
                padding: 0.35rem 0.55rem;
                font-size: 0.78rem;
                font-weight: 700;
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

            .st-key-pb_topbar {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                background: linear-gradient(180deg, rgba(17,19,24,0.96), rgba(13,17,23,0.96));
                padding: 0.75rem 1rem 0.45rem;
                margin-bottom: 1.3rem;
            }

            .st-key-pb_topbar [data-testid="stSelectbox"] {
                max-width: 420px;
            }

            .st-key-pb_topbar [data-testid="stWidgetLabel"] p {
                color: var(--pb-muted) !important;
                font-size: 0.78rem !important;
                font-weight: 650 !important;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .pb-project-table {
                border: 1px solid var(--pb-border);
                border-radius: 14px;
                overflow: hidden;
                margin-top: 0.65rem;
            }

            .pb-project-table-head {
                display: grid;
                grid-template-columns: 2.2fr 0.75fr 0.75fr 0.75fr 1fr;
                gap: 0.75rem;
                padding: 0.7rem 0.9rem;
                background: #18181B;
                border-bottom: 1px solid var(--pb-border);
                color: var(--pb-muted);
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            @media (max-width: 1200px) {
                .pb-project-table-head {
                    gap: 0.35rem;
                    padding-inline: 0.65rem;
                    font-size: 0.61rem;
                    letter-spacing: 0.02em;
                }

                [class*="st-key-pb_project_row_"] {
                    padding-inline: 0.6rem;
                }
            }

            [class*="st-key-pb_project_row_"] {
                border: 1px solid var(--pb-border);
                border-top: 0;
                background: rgba(17,19,24,0.82);
                padding: 0.55rem 0.85rem 0.35rem;
            }

            [class*="st-key-pb_project_row_"]:last-of-type {
                border-radius: 0 0 14px 14px;
            }

            .pb-table-project-name {
                color: #FAFAFA;
                font-weight: 750;
                line-height: 2.35rem;
            }

            .pb-table-cell {
                color: #D4D4D8;
                line-height: 2.35rem;
            }

            .pb-current-badge {
                display: inline-flex;
                margin-left: 0.45rem;
                padding: 0.12rem 0.4rem;
                border: 1px solid #52525B;
                border-radius: 999px;
                color: #A1A1AA;
                font-size: 0.68rem;
                font-weight: 650;
                vertical-align: middle;
            }

            .pb-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
            }

            .pb-compact-divider {
                height: 1px;
                margin: 0.8rem 0 0.65rem;
                background: rgba(255,255,255,0.08);
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
    st.markdown(
        f"""
        <style>
            :root {{
                --pb-bg: {'#F4F6F8' if light else '#09090B'};
                --pb-panel: {'#FFFFFF' if light else '#111318'};
                --pb-panel-2: {'#EEF1F5' if light else '#18181B'};
                --pb-border: {'#D6DAE1' if light else '#27272A'};
                --pb-text: {'#15171A' if light else '#FAFAFA'};
                --pb-text-2: {'#343840' if light else '#D4D4D8'};
                --pb-muted: {'#68707D' if light else '#A1A1AA'};
            }}

            .pb-brand-logo {{
                width: 36px;
                height: 36px;
                object-fit: cover;
                border-radius: 10px;
                border: 1px solid var(--pb-border);
            }}

            .pb-auth-logo {{
                width: 74px;
                height: 74px;
                border-radius: 22px;
                background: url('{logo}') center/cover no-repeat;
                box-shadow: 0 18px 50px rgba(0,0,0,.28);
            }}

            div[data-testid="stTextInput"] input[type="password"] {{
                padding-right: 3.4rem !important;
            }}

            .st-key-auth_google button::before,
            .st-key-auth_facebook button::before,
            .st-key-ui_v2_source_slack button::before,
            .st-key-ui_v2_source_jira button::before,
            .st-key-ui_v2_source_confluence button::before {{
                content: "";
                display: inline-flex;
                flex: 0 0 1.15rem;
                width: 1.15rem;
                height: 1.15rem;
                margin-right: .45rem;
                background: currentColor;
                mask-position: center;
                mask-repeat: no-repeat;
                mask-size: contain;
            }}
            .st-key-auth_google button::before {{ mask-image: url('{google_icon}'); }}
            .st-key-auth_facebook button::before {{ mask-image: url('{facebook_icon}'); }}
            .st-key-ui_v2_source_slack button::before {{ mask-image: url('{slack_icon}'); }}
            .st-key-ui_v2_source_jira button::before {{ mask-image: url('{jira_icon}'); }}
            .st-key-ui_v2_source_confluence button::before {{ mask-image: url('{confluence_icon}'); }}

            div[data-testid="stButton"] button,
            [data-testid="stFormSubmitButton"] button,
            div[data-testid="stExpander"],
            div[data-testid="stTabs"] button {{
                transition: transform .18s ease, background-color .22s ease,
                    border-color .22s ease, box-shadow .22s ease !important;
            }}
            div[data-testid="stButton"] button:hover,
            [data-testid="stFormSubmitButton"] button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 8px 24px rgba(0,0,0,.16) !important;
            }}
            div[data-testid="stExpander"] details[open] > div {{
                animation: pbReveal .24s ease both;
            }}
            .block-container {{ animation: pbPageIn .28s ease both; }}

            .pb-glass-loader {{
                position: fixed;
                inset: 0;
                z-index: 99999;
                display: grid;
                place-items: center;
                background: rgba(9,9,11,.72);
                backdrop-filter: blur(24px);
                animation: pbFadeIn .25s ease both;
            }}
            .pb-loader-card {{
                position: relative;
                width: min(520px, 86vw);
                min-height: 280px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255,255,255,.18);
                border-radius: 30px;
                background: linear-gradient(135deg,rgba(255,255,255,.14),rgba(255,255,255,.04));
                box-shadow: 0 30px 100px rgba(0,0,0,.45);
                overflow: hidden;
            }}
            .pb-loader-card img {{ width: 92px; height: 92px; border-radius: 28px; object-fit: cover; }}
            .pb-loader-orbit {{
                position: absolute;
                width: 126px;
                height: 126px;
                border: 2px solid transparent;
                border-top-color: #FF4B4B;
                border-radius: 50%;
                animation: pbSpin 1.1s linear infinite;
            }}
            .pb-loader-messages {{ position: relative; width: 100%; height: 52px; margin-top: 34px; }}
            .pb-loader-messages span {{
                position: absolute;
                inset: 0;
                color: #FAFAFA;
                text-align: center;
                opacity: 0;
                animation: pbMessage 2.7s ease infinite;
            }}
            .pb-loader-messages span:nth-child(2) {{ animation-delay: .9s; }}
            .pb-loader-messages span:nth-child(3) {{ animation-delay: 1.8s; }}
            .pb-route-loader {{ display:flex; justify-content:center; gap:7px; padding:1rem; }}
            .pb-route-loader span {{ width:8px; height:8px; border-radius:50%; background:#FF4B4B; animation:pbDot .7s ease infinite alternate; }}
            .pb-route-loader span:nth-child(2) {{ animation-delay:.14s; }}
            .pb-route-loader span:nth-child(3) {{ animation-delay:.28s; }}

            {light_overrides}

            @keyframes pbSpin {{ to {{ transform: rotate(360deg); }} }}
            @keyframes pbFadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
            @keyframes pbPageIn {{ from {{ opacity:.2; transform:translateY(7px); }} to {{ opacity:1; transform:none; }} }}
            @keyframes pbReveal {{ from {{ opacity:0; transform:translateY(-6px); }} to {{ opacity:1; transform:none; }} }}
            @keyframes pbDot {{ to {{ transform:translateY(-7px); opacity:.45; }} }}
            @keyframes pbMessage {{ 0%,100% {{ opacity:0; transform:translateY(7px); }} 15%,28% {{ opacity:1; transform:none; }} 40% {{ opacity:0; transform:translateY(-7px); }} }}

            @media (max-width: 980px) {{
                .block-container {{ padding: .75rem !important; }}
                [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; gap: .6rem !important; }}
                [data-testid="stHorizontalBlock"] > div {{ min-width: min(100%, 240px) !important; flex: 1 1 240px !important; }}
                .st-key-pb_navigation div[data-testid="stButton"] button {{ font-size: .76rem !important; }}
                .pb-project-table-head {{ display:none; }}
            }}
            @media (max-width: 640px) {{
                h1 {{ font-size: 2rem !important; }}
                .pb-brand-title, .pb-caption {{ display:none; }}
                .pb-brand {{ justify-content:center; }}
                .pb-loader-card {{ min-height:240px; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
