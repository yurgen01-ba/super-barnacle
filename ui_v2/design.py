import streamlit as st
from ui_v2.assets import logo_data_uri, nav_icon_data_uri, svg_data_uri


def inject_ui_v2_theme(theme: str = "dark"):
    light = theme == "light"
    logo = logo_data_uri()
    google_icon = svg_data_uri("google")
    facebook_icon = svg_data_uri("facebook")
    slack_icon = svg_data_uri("slack")
    jira_icon = svg_data_uri("jira")
    confluence_icon = svg_data_uri("confluence")
    nav_icons = {
        name: nav_icon_data_uri(name)
        for name in (
            "projects", "workspace", "sources", "participants", "speech",
            "artifacts", "exports", "meetings", "files", "settings", "model",
        )
    }
    light_overrides = """
        .st-key-pb_navigation div[data-testid="stButton"] button,
        .st-key-pb_navigation div[data-testid="stButton"] button p,
        .st-key-pb_navigation div[data-testid="stButton"] button span {
            color: #343840 !important;
            -webkit-text-fill-color: #343840 !important;
        }
        .st-key-pb_navigation div[data-testid="stButton"] button:hover,
        .st-key-pb_navigation div[data-testid="stButton"] button:hover p,
        .st-key-pb_navigation div[data-testid="stButton"] button:hover span {
            color: #15171A !important;
            -webkit-text-fill-color: #15171A !important;
        }
        .st-key-pb_navigation div[data-testid="stButton"] button::before,
        .st-key-pb_navigation div[data-testid="stButton"] button:hover::before {
            background-color: #343840 !important;
            color: #343840 !important;
        }
        .st-key-pb_navigation div[data-testid="stButton"] button[kind="primary"],
        .st-key-pb_navigation div[data-testid="stButton"] button[kind="primary"] p {
            color: #15171A !important;
            background: #E5E9EF !important;
        }
        div[data-testid="stButton"] button:not([kind="primary"]),
        [data-testid="stFormSubmitButton"] button:not([kind*="primary"]) {
            background: #FFFFFF !important;
            color: #343840 !important;
            -webkit-text-fill-color: #343840 !important;
            border-color: #D6DAE1 !important;
        }
        div[data-testid="stButton"] button:not([kind="primary"]) *,
        [data-testid="stFormSubmitButton"] button:not([kind*="primary"]) * {
            background: transparent !important;
            color: #343840 !important;
            -webkit-text-fill-color: #343840 !important;
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
        html body div[data-testid="stExpander"],
        html body div[data-testid="stExpander"] details,
        html body div[data-testid="stExpander"] summary,
        html body details[data-testid="stExpander"],
        html body details[data-testid="stExpander"] > summary,
        html body details[data-testid="stExpander"] > div,
        .st-key-pb_topbar,
        .pb-panel,
        .pb-source-card,
        .pb-chat-bubble {
            background: #FFFFFF !important;
            color: #15171A !important;
            border-color: #D6DAE1 !important;
        }
        html body details[data-testid="stExpander"] > summary *,
        html body div[data-testid="stExpander"] summary * {
            background: transparent !important;
            color: #343840 !important;
            -webkit-text-fill-color: #343840 !important;
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
                padding: 0.45rem 1.4rem 2rem !important;
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

            div[data-testid="stTabs"] [role="tablist"] {
                display: flex !important;
                width: 100% !important;
            }

            div[data-testid="stTabs"] [role="tab"] {
                flex: 1 1 0 !important;
                justify-content: center !important;
                text-align: center !important;
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
                background: transparent !important;
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
                justify-content: flex-end;
                min-height: 2.55rem;
                gap: 0.65rem;
                transform: translateY(-0.32rem);
                white-space: nowrap;
            }

            .st-key-pb_topbar [data-testid="stMarkdownContainer"] p {
                margin: 0 !important;
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
                align-items: center;
                margin-left: 0.45rem;
                padding: 0.18rem 0.45rem;
                min-height: 0 !important;
                height: 1.35rem !important;
                max-height: 1.35rem !important;
                box-sizing: border-box !important;
                line-height: 1.05 !important;
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
                min-height: 72px;
                display: flex;
                align-items: center;
            }

            .pb-source-title {
                color: white;
                font-weight: 720;
                display: flex;
                align-items: center;
                gap: 0.7rem;
                margin: 0;
            }

            .pb-source-icon {
                display: inline-block;
                width: 1.1em;
                height: 1.1em;
                flex: 0 0 1.1em;
                background: currentColor;
                -webkit-mask: var(--pb-source-icon-url) center / contain no-repeat;
                mask: var(--pb-source-icon-url) center / contain no-repeat;
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
                width: 42px;
                height: 42px;
                border-radius: 12px;
                border: 1px solid var(--pb-border);
                box-shadow: 0 10px 30px rgba(0,0,0,.24);
                background: var(--pb-bg);
                overflow: hidden;
                position: relative;
            }}

            .pb-auth-logo {{
                width: 74px;
                height: 74px;
                border-radius: 22px;
                background: var(--pb-bg);
                box-shadow: 0 18px 50px rgba(0,0,0,.28);
                overflow: hidden;
                position: relative;
            }}

            .st-key-pb_preferences_toolbar,
            .st-key-pb_topbar_preferences {{
                width: fit-content !important;
                margin-left: auto !important;
                margin-right: 1rem !important;
                padding: .18rem !important;
                border: 1px solid var(--pb-border) !important;
                border-radius: 12px !important;
                background: var(--pb-panel) !important;
                box-shadow: 0 8px 26px rgba(0,0,0,.12);
            }}

            .st-key-pb_preferences_toolbar [data-testid="stHorizontalBlock"],
            .st-key-pb_topbar_preferences [data-testid="stHorizontalBlock"] {{
                gap: 0 !important;
                flex-wrap: nowrap !important;
            }}

            .st-key-pb_preferences_toolbar [data-testid="stHorizontalBlock"] > div,
            .st-key-pb_topbar_preferences [data-testid="stHorizontalBlock"] > div {{
                width: 2.25rem !important;
                min-width: 2.25rem !important;
                max-width: 2.25rem !important;
                flex: 0 0 2.25rem !important;
            }}

            .st-key-pb_preferences_toolbar button,
            .st-key-pb_topbar_preferences button {{
                width: 2.25rem !important;
                min-width: 2.25rem !important;
                height: 2.25rem !important;
                min-height: 2.25rem !important;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 9px !important;
                background: transparent !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            .st-key-pb_preferences_toolbar button:hover,
            .st-key-pb_topbar_preferences button:hover {{
                background: rgba(127,127,127,.12) !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            .st-key-pb_topbar {{
                padding: .62rem .8rem .38rem !important;
                margin-bottom: 1rem !important;
                background: var(--pb-panel) !important;
            }}

            .st-key-pb_topbar_preferences {{
                margin-right: 0 !important;
            }}

            .st-key-pb_user_controls {{
                padding: .38rem .5rem !important;
                margin: 0 0 .6rem 0 !important;
                border: 0 !important;
                background: transparent !important;
            }}

            .pb-user-inline {{
                min-height: 46px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: .52rem;
                white-space: nowrap;
            }}

            .pb-user-avatar {{
                width: 42px !important;
                height: 42px !important;
                flex: 0 0 42px;
                border-radius: 50% !important;
                object-fit: cover !important;
                border: 1px solid var(--pb-border) !important;
            }}

            .pb-user-inline .pb-account-link,
            .pb-user-inline .pb-logout-link {{
                display: inline-flex !important;
                width: auto !important;
                min-width: 0 !important;
                padding: 0 !important;
                font-size: .84rem !important;
                font-weight: 560;
                line-height: 1;
                text-decoration: none !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }}

            .pb-user-inline .pb-account-link {{
                color: var(--pb-text-2) !important;
            }}

            .pb-user-inline .pb-logout-link {{
                color: var(--pb-red) !important;
            }}

            .pb-user-inline .pb-account-link:hover,
            .pb-user-inline .pb-logout-link:hover {{
                text-decoration: none !important;
                opacity: .72;
            }}

            .pb-pref-links {{
                display: inline-flex;
                align-items: center;
                padding: 2px;
                margin-left: .12rem;
                border: 1px solid var(--pb-border);
                border-radius: 10px;
                background: var(--pb-panel);
            }}

            .pb-pref-links a {{
                display: inline-flex !important;
                align-items: center;
                justify-content: center;
                width: 30px !important;
                min-width: 30px !important;
                height: 30px !important;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 8px !important;
                background: transparent !important;
                box-shadow: none !important;
                color: var(--pb-text-2) !important;
                text-decoration: none !important;
                font-size: .9rem !important;
            }}

            .pb-pref-links a + a {{
                border-left: 1px solid var(--pb-border) !important;
                border-radius: 0 8px 8px 0 !important;
            }}

            .pb-pref-links a:hover {{
                background: var(--pb-panel-2) !important;
            }}

            h1 {{
                font-size: clamp(2rem, 3vw, 2.65rem) !important;
                line-height: 1.08 !important;
                letter-spacing: -.035em !important;
                margin: 0 0 .65rem !important;
            }}

            h2 {{
                font-size: clamp(1.45rem, 2vw, 1.8rem) !important;
                line-height: 1.18 !important;
                letter-spacing: -.02em !important;
                margin: .8rem 0 .55rem !important;
            }}

            h3, h4 {{
                font-size: 1.18rem !important;
                line-height: 1.25 !important;
                letter-spacing: -.01em !important;
                margin: .65rem 0 .45rem !important;
            }}

            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] p {{
                color: var(--pb-muted) !important;
                font-size: .84rem !important;
                line-height: 1.45 !important;
            }}

            .pb-project-table,
            .pb-project-table-head,
            [class*="st-key-pb_project_row_"] {{
                border-color: var(--pb-border) !important;
            }}

            .pb-project-table-head {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-muted) !important;
            }}

            [class*="st-key-pb_project_row_"] {{
                background: var(--pb-panel) !important;
            }}

            .pb-table-project-name,
            .pb-table-cell {{
                color: var(--pb-text-2) !important;
            }}

            .pb-current-badge {{
                color: var(--pb-muted) !important;
                border-color: var(--pb-border) !important;
                background: var(--pb-panel-2) !important;
            }}

            [class*="st-key-project_settings_"] [data-testid="stButton"] {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }}

            [class*="st-key-project_settings_"] [data-testid="stButton"] button,
            [class*="st-key-project_settings_"] [data-testid="stButton"] button:hover,
            [class*="st-key-project_settings_"] [data-testid="stButton"] button:focus,
            [class*="st-key-project_settings_"] [data-testid="stButton"] button:active {{
                width: 2.5rem !important;
                min-width: 2.5rem !important;
                height: 2.5rem !important;
                min-height: 2.5rem !important;
                padding: 0 !important;
                margin: 0 auto !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 0 !important;
                border: 0 !important;
                outline: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }}

            [class*="st-key-project_settings_"] [data-testid="stButton"] button p {{
                display: none !important;
            }}

            [class*="st-key-project_settings_"] [data-testid="stButton"] button [data-testid="stIconMaterial"] {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                margin: 0 !important;
                line-height: 1 !important;
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            [class*="st-key-source_auth_panel_"] {{
                min-height: 18rem !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
            }}

            [class*="st-key-source_auth_panel_"] [data-testid="stButton"] {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
            }}

            div[data-testid="stExpander"],
            div[data-testid="stExpander"] details,
            div[data-testid="stExpander"] summary {{
                background: var(--pb-panel) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            div[data-testid="stExpander"] summary * {{
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            div[data-testid="stButton"] button:disabled,
            div[data-testid="stButton"] button:disabled * {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-muted) !important;
                -webkit-text-fill-color: var(--pb-muted) !important;
                border-color: var(--pb-border) !important;
                opacity: .72 !important;
            }}

            .pb-member-name {{
                color: var(--pb-text) !important;
                font-size: .94rem !important;
                font-weight: 700;
                margin-bottom: .18rem;
            }}

            .pb-member-meta,
            .pb-member-status {{
                color: var(--pb-muted) !important;
                font-size: .8rem !important;
                line-height: 1.35;
                overflow-wrap: anywhere;
            }}

            div[data-testid="stMetric"],
            .pb-panel,
            .pb-source-card,
            .pb-menu-block,
            .pb-project-card,
            .pb-chat-bubble {{
                background: var(--pb-panel) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            div[data-testid="stButton"] button:not([kind="primary"]),
            [data-testid="stFormSubmitButton"] button:not([kind*="primary"]),
            [data-testid="stDownloadButton"] button {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            div[data-testid="stButton"] button *,
            [data-testid="stFormSubmitButton"] button *,
            [data-testid="stDownloadButton"] button * {{
                background: transparent !important;
            }}

            .st-key-pb_navigation div[data-testid="stButton"] button::before,
            .st-key-ui_v2_source_meetings button::before,
            .st-key-ui_v2_source_files button::before,
            .st-key-ui_v2_source_slack button::before,
            .st-key-ui_v2_source_jira button::before,
            .st-key-ui_v2_source_confluence button::before {{
                background-color: currentColor !important;
                color: inherit !important;
                opacity: 1 !important;
            }}

            details[data-testid="stExpander"],
            details[data-testid="stExpander"] > summary,
            details[data-testid="stExpander"][open] > summary,
            details[data-testid="stExpander"] > div,
            details[data-testid="stExpander"] > summary:hover {{
                background: var(--pb-panel) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            details[data-testid="stExpander"] > summary * {{
                background: transparent !important;
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            [data-testid="stAppViewContainer"] > .main,
            [data-testid="stMain"],
            [data-testid="stAppViewBlockContainer"],
            [data-testid="stMainBlockContainer"],
            .block-container {{
                margin-top: 0 !important;
                padding-top: .25rem !important;
            }}

            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
                gap: 0 !important;
            }}

            .st-key-pb_user_controls [data-testid="stHorizontalBlock"] {{
                justify-content: flex-end !important;
                align-items: center !important;
                flex-wrap: nowrap !important;
                gap: .3rem !important;
            }}

            .st-key-pb_user_controls img {{
                width: 42px !important;
                height: 42px !important;
                border-radius: 50% !important;
                object-fit: cover !important;
            }}

            .st-key-open_user_profile button,
            .st-key-auth_logout button {{
                width: auto !important;
                min-height: 2rem !important;
                padding: 0 .12rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }}

            .st-key-open_user_profile button:hover,
            .st-key-auth_logout button:hover {{
                background: transparent !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            .st-key-open_user_profile button p {{
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
                text-decoration: none !important;
                white-space: nowrap !important;
            }}

            .st-key-auth_logout button p {{
                color: #FF4B4B !important;
                -webkit-text-fill-color: #FF4B4B !important;
                text-decoration: none !important;
                white-space: nowrap !important;
            }}

            .st-key-pb_language_cycle button,
            .st-key-pb_theme_toggle button {{
                width: 32px !important;
                min-width: 32px !important;
                height: 32px !important;
                min-height: 32px !important;
                padding: 0 !important;
                border-radius: 8px !important;
                background: var(--pb-panel-2) !important;
                color: var(--pb-text-2) !important;
            }}

            div[data-testid="stTextArea"] textarea,
            div[data-testid="stTextInput"] input,
            div[data-testid="stSelectbox"] div[data-baseweb="select"],
            div[data-testid="stSelectbox"] [role="group"],
            div[data-testid="stSelectbox"] input[role="combobox"] {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text) !important;
                -webkit-text-fill-color: var(--pb-text) !important;
                border-color: var(--pb-border) !important;
            }}

            div[data-testid="stTabs"] button {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-muted) !important;
                border-color: var(--pb-border) !important;
            }}

            div[data-testid="stTabs"] button[aria-selected="true"],
            div[data-testid="stTabs"] button[aria-selected="true"] * {{
                color: var(--pb-text) !important;
                -webkit-text-fill-color: var(--pb-text) !important;
            }}

            div[data-testid="stFileUploader"],
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stFileUploaderDropzone"] > div,
            div[data-testid="stFileUploader"] section {{
                background: var(--pb-panel) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            [data-testid="stFileUploaderDropzone"] button,
            [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            [data-testid="stFileUploaderDropzone"] button *,
            [data-testid="stFileUploaderDropzoneInstructions"],
            [data-testid="stFileUploaderDropzoneInstructions"] * {{
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            div[data-testid="stJson"],
            div[data-testid="stJson"] > div,
            div[data-testid="stJson"] pre,
            div[data-testid="stJson"] .react-json-view,
            div[data-baseweb="popover"],
            div[data-baseweb="menu"],
            [data-testid="stSelectboxVirtualDropdown"],
            [role="listbox"],
            [role="option"],
            [role="option"] > div {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            [role="option"][data-focused="true"],
            [role="option"][aria-selected="true"],
            [role="option"]:hover,
            [role="option"][data-focused="true"] > div,
            [role="option"][aria-selected="true"] > div,
            [role="option"]:hover > div {{
                background: var(--pb-panel) !important;
                color: var(--pb-text) !important;
                -webkit-text-fill-color: var(--pb-text) !important;
            }}

            [data-testid="stCheckbox"] label:not([data-selected="true"]) > div:first-of-type,
            [data-testid="stRadioOption"]:not([data-selected="true"]) > div > div > div:first-child,
            [data-testid="stRadioOption"]:not([data-selected="true"]) > div > div > div:first-child > div {{
                background: var(--pb-panel-2) !important;
                border-color: var(--pb-border) !important;
            }}

            [role="tooltip"],
            [data-testid="stTooltipContent"] {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            [data-testid="stTooltipContent"] *,
            [role="tooltip"] * {{
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            .pb-brand-logo img,
            .pb-auth-logo img,
            .pb-loader-logo img {{
                position: absolute;
                left: 50%;
                top: 50%;
                width: 150%;
                height: 150%;
                max-width: none !important;
                object-fit: cover;
                transform: translate(-50%, -50%);
                filter: {'invert(1)' if light else 'none'};
                mix-blend-mode: {'multiply' if light else 'screen'};
            }}

            div[data-testid="stTextInput"] input[type="password"] {{
                padding-right: 3.4rem !important;
            }}

            div[data-testid="stTextInput"] [data-baseweb="input"] {{
                overflow: hidden !important;
                border: 1px solid var(--pb-border) !important;
                border-radius: 10px !important;
                background: {'#FFFFFF' if light else 'rgba(24,24,27,.96)'} !important;
                box-shadow: none !important;
            }}

            div[data-testid="stTextInput"] [data-baseweb="input"] input {{
                border: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }}

            html body div.stApp div[data-testid="stTextInput"] button {{
                width: 3rem !important;
                min-width: 3rem !important;
                height: 2.7rem !important;
                padding: 0 !important;
                margin: 0 !important;
                border: 0 !important;
                border-radius: 0 9px 9px 0 !important;
                background: transparent !important;
                color: var(--pb-muted) !important;
                border-left: 1px solid var(--pb-border) !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            html body div.stApp div[data-testid="stTextInput"] button:hover {{
                background: color-mix(in srgb, var(--pb-text-2) 8%, transparent) !important;
                color: var(--pb-text) !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            html body div.stApp div[data-testid="stTextInput"] button svg,
            html body div.stApp div[data-testid="stTextInput"] button:hover svg {{
                color: currentColor !important;
                fill: none !important;
                stroke: currentColor !important;
                opacity: 1 !important;
            }}

            .st-key-auth_google button::before,
            .st-key-auth_facebook button::before,
            .st-key-ui_v2_nav_projects button::before,
            .st-key-ui_v2_nav_dashboard button::before,
            .st-key-ui_v2_nav_sources button::before,
            .st-key-ui_v2_nav_participants button::before,
            .st-key-ui_v2_nav_transcription_diagnostics button::before,
            .st-key-ui_v2_nav_artifacts button::before,
            .st-key-ui_v2_nav_exports button::before,
            .st-key-ui_v2_source_meetings button::before,
            .st-key-ui_v2_source_files button::before,
            .st-key-ui_v2_nav_settings button::before,
            .st-key-ui_v2_nav_project_model button::before,
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
                color: inherit;
                mask-position: center;
                mask-repeat: no-repeat;
                mask-size: contain;
            }}
            .st-key-auth_google button::before {{ mask-image: url('{google_icon}'); }}
            .st-key-auth_facebook button::before {{ mask-image: url('{facebook_icon}'); }}
            .st-key-ui_v2_nav_projects button::before {{ mask-image: url('{nav_icons['projects']}'); }}
            .st-key-ui_v2_nav_dashboard button::before {{ mask-image: url('{nav_icons['workspace']}'); }}
            .st-key-ui_v2_nav_sources button::before {{ mask-image: url('{nav_icons['sources']}'); }}
            .st-key-ui_v2_nav_participants button::before {{ mask-image: url('{nav_icons['participants']}'); }}
            .st-key-ui_v2_nav_transcription_diagnostics button::before {{ mask-image: url('{nav_icons['speech']}'); }}
            .st-key-ui_v2_nav_artifacts button::before {{ mask-image: url('{nav_icons['artifacts']}'); }}
            .st-key-ui_v2_nav_exports button::before {{ mask-image: url('{nav_icons['exports']}'); }}
            .st-key-ui_v2_source_meetings button::before {{ mask-image: url('{nav_icons['meetings']}'); }}
            .st-key-ui_v2_source_files button::before {{ mask-image: url('{nav_icons['files']}'); }}
            .st-key-ui_v2_nav_settings button::before {{ mask-image: url('{nav_icons['settings']}'); }}
            .st-key-ui_v2_nav_project_model button::before {{ mask-image: url('{nav_icons['model']}'); }}
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
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                background:
                    radial-gradient(circle at 18% 22%, rgba(255,75,75,.18), transparent 34%),
                    radial-gradient(circle at 82% 76%, rgba(59,130,246,.16), transparent 36%),
                    rgba(9,9,11,.76);
                backdrop-filter: blur(30px) saturate(145%);
                -webkit-backdrop-filter: blur(30px) saturate(145%);
                animation: pbFadeIn .25s ease both;
            }}
            .pb-glass-loader::before {{
                content: "";
                position: absolute;
                inset: -45%;
                background: linear-gradient(
                    112deg,
                    transparent 38%,
                    rgba(255,255,255,.04) 44%,
                    rgba(255,255,255,.26) 50%,
                    rgba(255,255,255,.05) 56%,
                    transparent 62%
                );
                transform: translateX(-38%) rotate(4deg);
                animation: pbGlassSweep 2.4s ease-in-out infinite;
                pointer-events: none;
            }}
            .pb-loader-card {{
                position: relative;
                width: 100vw;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border: 0;
                border-radius: 0;
                background: linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.015));
                box-shadow: inset 0 0 120px rgba(255,255,255,.035);
                overflow: hidden;
            }}
            .pb-loader-mark {{
                position: relative;
                display: grid;
                place-items: center;
                flex: 0 0 168px;
                width: 168px;
                height: 168px;
                margin-bottom: 3rem;
            }}
            .pb-loader-logo {{
                position: relative;
                z-index: 2;
                width: 138px;
                height: 138px;
                border-radius: 42px;
                overflow: hidden;
                background: var(--pb-bg);
            }}
            .pb-loader-logo img {{
                display: block;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .pb-loader-trace {{
                position: absolute;
                inset: 0;
                z-index: 3;
                border-radius: inherit;
                background: linear-gradient(
                    105deg,
                    transparent 0%,
                    transparent 38%,
                    rgba(255,75,75,.35) 44%,
                    #FF4B4B 50%,
                    rgba(255,75,75,.35) 56%,
                    transparent 62%,
                    transparent 100%
                );
                background-size: 320% 100%;
                background-position: 135% 0;
                mix-blend-mode: {'screen' if light else 'multiply'};
                animation: pbLogoTrace 1.8s ease-in-out infinite;
                pointer-events: none;
            }}
            .pb-loader-messages {{
                position: relative;
                flex: 0 0 112px;
                width: min(980px, 88vw);
                height: 112px;
                margin: 0;
            }}
            .pb-loader-messages span {{
                position: absolute;
                inset: 0;
                color: #FAFAFA;
                text-align: center;
                font-size: clamp(1.7rem, 4vw, 3.5rem);
                line-height: 1.12;
                font-weight: 760;
                letter-spacing: -.035em;
                text-shadow: 0 10px 45px rgba(0,0,0,.45);
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

            /* The source card itself is the control; there is no nested
               open/collapse button. */
            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button {{
                width: 100% !important;
                min-height: 76px !important;
                padding: 1rem !important;
                justify-content: flex-start !important;
                gap: .7rem !important;
                border: 1px solid var(--pb-border) !important;
                border-radius: 16px !important;
                background: var(--pb-panel) !important;
                color: var(--pb-text) !important;
                box-shadow: none !important;
                transform: none !important;
                cursor: pointer !important;
                transition: background-color .2s ease, border-color .2s ease,
                    box-shadow .2s ease, transform .2s ease !important;
            }}

            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button:hover {{
                background: var(--pb-panel-2) !important;
                color: var(--pb-text) !important;
                border-color: color-mix(in srgb, var(--pb-text-2) 32%, var(--pb-border)) !important;
            }}

            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button[kind="primary"],
            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button[kind="primary"]:hover {{
                background: color-mix(in srgb, #3B82F6 14%, var(--pb-panel)) !important;
                border-color: rgba(59, 130, 246, .72) !important;
                box-shadow: 0 0 0 1px rgba(59, 130, 246, .14),
                    0 10px 30px rgba(59, 130, 246, .10) !important;
            }}

            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button::before {{
                content: "";
                display: inline-flex;
                flex: 0 0 1.15rem;
                width: 1.15rem;
                height: 1.15rem;
                background: currentColor !important;
                mask-position: center;
                mask-repeat: no-repeat;
                mask-size: contain;
            }}

            [class*="st-key-pb_source_card_meetings"] button::before {{ mask-image: url('{nav_icons['meetings']}'); }}
            [class*="st-key-pb_source_card_slack"] button::before {{ mask-image: url('{slack_icon}'); }}
            [class*="st-key-pb_source_card_confluence"] button::before {{ mask-image: url('{confluence_icon}'); }}
            [class*="st-key-pb_source_card_jira"] button::before {{ mask-image: url('{jira_icon}'); }}

            html body [class*="st-key-pb_source_card_"] [data-testid="stButton"] button p {{
                margin: 0 !important;
                color: currentColor !important;
                -webkit-text-fill-color: currentColor !important;
                font-weight: 720 !important;
            }}

            /* Streamlit adds its own dark hover to expander summaries.  Keep
               all expander states inside the active application theme. */
            html body div[data-testid="stExpander"],
            html body div[data-testid="stExpander"] > details,
            html body div[data-testid="stExpander"] > details > summary,
            html body div[data-testid="stExpander"] > details > summary:hover,
            html body div[data-testid="stExpander"] > details[open] > summary,
            html body div[data-testid="stExpander"] > details > div {{
                background: var(--pb-panel) !important;
                color: var(--pb-text-2) !important;
                border-color: var(--pb-border) !important;
            }}

            html body div[data-testid="stExpander"] > details > summary:hover {{
                background: var(--pb-panel-2) !important;
            }}

            html body div[data-testid="stExpander"] > details > summary *,
            html body div[data-testid="stExpander"] > details > summary:hover * {{
                background: transparent !important;
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            .st-key-pb_user_controls [data-testid="stHorizontalBlock"] {{
                justify-content: flex-end !important;
                align-items: center !important;
                flex-wrap: nowrap !important;
                gap: .42rem !important;
            }}

            .st-key-pb_user_controls [data-testid="stHorizontalBlock"] > div {{
                flex: 0 0 auto !important;
                width: auto !important;
                min-width: 0 !important;
            }}

            html body .st-key-open_user_profile div[data-testid="stButton"] button,
            html body .st-key-auth_logout div[data-testid="stButton"] button {{
                width: auto !important;
                min-width: 0 !important;
                min-height: 1.8rem !important;
                padding: 0 .08rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
                transform: none !important;
            }}

            html body .st-key-open_user_profile div[data-testid="stButton"] button *,
            html body .st-key-auth_logout div[data-testid="stButton"] button * {{
                background: transparent !important;
                text-decoration: none !important;
            }}

            html body .st-key-open_user_profile div[data-testid="stButton"] button p {{
                color: var(--pb-text-2) !important;
                -webkit-text-fill-color: var(--pb-text-2) !important;
            }}

            html body .st-key-auth_logout div[data-testid="stButton"] button p {{
                color: #FF4B4B !important;
                -webkit-text-fill-color: #FF4B4B !important;
            }}

            .pb-project-label {{
                display: flex;
                align-items: center;
                min-height: 2.55rem;
                color: var(--pb-muted) !important;
                font-size: .78rem !important;
                font-weight: 750;
                letter-spacing: .06em;
                text-transform: uppercase;
                white-space: nowrap;
                transform: translateY(-0.32rem);
            }}

            .st-key-pb_topbar [data-testid="stSelectbox"] {{
                margin: 0 !important;
            }}

            @keyframes pbLogoTrace {{
                0% {{ background-position: 135% 0; opacity: .25; }}
                18% {{ opacity: 1; }}
                82% {{ opacity: 1; }}
                100% {{ background-position: -35% 0; opacity: .25; }}
            }}
            @keyframes pbGlassSweep {{
                0% {{ transform: translateX(-42%) rotate(4deg); opacity:.35; }}
                50% {{ opacity:1; }}
                100% {{ transform: translateX(42%) rotate(4deg); opacity:.35; }}
            }}
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
                .pb-loader-card {{ min-height:240px; padding: 2rem 1rem; }}
                .pb-loader-mark {{ margin-bottom: 3.5rem; }}
                .pb-loader-messages {{ width: 88vw; height: 136px; flex-basis: 136px; }}
                .pb-loader-messages span {{ font-size: clamp(1.45rem, 8vw, 2.15rem); }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
