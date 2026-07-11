import streamlit as st


def inject_project_brain_theme():
    """
    Lightweight Streamlit UI polish.

    Goal:
    - keep Streamlit for now;
    - make UI darker, tighter, more product-like;
    - avoid a risky React/FastAPI migration while the intelligence core is still evolving.
    """
    st.markdown(
        """
        <style>
            :root {
                --pb-bg: #080b12;
                --pb-panel: #0f1420;
                --pb-panel-2: #111827;
                --pb-border: rgba(148, 163, 184, 0.18);
                --pb-text: #e5e7eb;
                --pb-muted: #94a3b8;
                --pb-accent: #38bdf8;
                --pb-positive: #22c55e;
                --pb-warning: #f59e0b;
                --pb-danger: #ef4444;
            }

            .stApp {
                background:
                    radial-gradient(circle at 20% 0%, rgba(56, 189, 248, 0.12), transparent 32%),
                    radial-gradient(circle at 80% 10%, rgba(34, 197, 94, 0.08), transparent 26%),
                    var(--pb-bg);
                color: var(--pb-text);
            }

            [data-testid="stHeader"] {
                background: rgba(8, 11, 18, 0.72);
                backdrop-filter: blur(16px);
                border-bottom: 1px solid var(--pb-border);
            }

            [data-testid="stToolbar"] {
                right: 1rem;
            }

            .block-container {
                padding-top: 2rem;
                max-width: 1380px;
            }

            h1, h2, h3 {
                letter-spacing: -0.035em;
            }

            div[data-testid="stTabs"] button {
                border-radius: 999px;
                border: 1px solid var(--pb-border);
                background: rgba(15, 20, 32, 0.62);
                color: var(--pb-muted);
                padding: 0.35rem 0.9rem;
                margin-right: 0.35rem;
            }

            div[data-testid="stTabs"] button[aria-selected="true"] {
                color: white;
                border-color: rgba(56, 189, 248, 0.55);
                background: rgba(56, 189, 248, 0.14);
            }

            div[data-testid="stExpander"] {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                background: rgba(15, 20, 32, 0.60);
                overflow: hidden;
            }

            div[data-testid="stMetric"] {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                background: rgba(15, 20, 32, 0.74);
            }

            div[data-testid="stDataFrame"] {
                border: 1px solid var(--pb-border);
                border-radius: 16px;
                overflow: hidden;
            }

            .pb-card {
                border: 1px solid var(--pb-border);
                background:
                    linear-gradient(180deg, rgba(17, 24, 39, 0.92), rgba(15, 20, 32, 0.78));
                border-radius: 20px;
                padding: 1rem 1.1rem;
                box-shadow: 0 18px 50px rgba(0, 0, 0, 0.20);
                margin-bottom: 0.85rem;
            }

            .pb-card-title {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                font-size: 1rem;
                font-weight: 700;
                color: var(--pb-text);
                margin-bottom: 0.25rem;
            }

            .pb-card-caption {
                color: var(--pb-muted);
                font-size: 0.86rem;
                line-height: 1.45;
            }

            .pb-pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.4rem;
                margin-top: 0.65rem;
            }

            .pb-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
                padding: 0.22rem 0.55rem;
                border: 1px solid var(--pb-border);
                border-radius: 999px;
                color: var(--pb-muted);
                font-size: 0.78rem;
                background: rgba(8, 11, 18, 0.35);
            }

            .pb-hero {
                border: 1px solid var(--pb-border);
                border-radius: 24px;
                padding: 1.2rem 1.35rem;
                background:
                    linear-gradient(135deg, rgba(56, 189, 248, 0.14), rgba(34, 197, 94, 0.08)),
                    rgba(15, 20, 32, 0.82);
                margin-bottom: 1rem;
            }

            .pb-hero-title {
                font-size: 1.35rem;
                font-weight: 800;
                letter-spacing: -0.04em;
                margin-bottom: 0.2rem;
            }

            .pb-hero-caption {
                color: var(--pb-muted);
                font-size: 0.92rem;
            }

            .pb-subtle {
                color: var(--pb-muted);
                font-size: 0.85rem;
            }

            .pb-section-label {
                color: var(--pb-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.72rem;
                font-weight: 700;
                margin-bottom: 0.45rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, caption: str, pills: list[str] | None = None):
    pills = pills or []

    pill_html = ""
    if pills:
        pill_html = "<div class='pb-pill-row'>" + "".join(
            f"<span class='pb-pill'>{pill}</span>" for pill in pills
        ) + "</div>"

    st.markdown(
        f"""
        <div class="pb-hero">
            <div class="pb-hero-title">{title}</div>
            <div class="pb-hero-caption">{caption}</div>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, caption: str = "", pills: list[str] | None = None):
    pills = pills or []

    pill_html = ""
    if pills:
        pill_html = "<div class='pb-pill-row'>" + "".join(
            f"<span class='pb-pill'>{pill}</span>" for pill in pills
        ) + "</div>"

    st.markdown(
        f"""
        <div class="pb-card">
            <div class="pb-card-title">
                <span>{title}</span>
            </div>
            <div class="pb-card-caption">{caption}</div>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_settings_expander(label: str = "⚙ Settings", expanded: bool = False):
    return st.expander(label, expanded=expanded)

