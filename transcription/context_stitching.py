from __future__ import annotations


DEFAULT_GLOSSARY_TERMS = [
    "Jira",
    "Confluence",
    "OrgMeter",
    "Bizcap",
    "Equifax",
    "Advance",
    "Funder",
    "Merchant",
    "Underwriter",
    "Syndicator",
    "Referrer",
    "task",
    "ticket",
    "scope",
    "speaker",
    "problem",
    "info panel",
    "discount",
    "field",
    "screen",
    "flow",
    "status",
    "pipeline",
    "dashboard",
    "button",
    "tab",
    "modal",
    "tooltip",
    "title",
    "section",
    "layout",
    "API",
    "endpoint",
    "backend",
    "frontend",
]


def build_initial_prompt(
    previous_text: str = "",
    glossary_terms: list[str] | None = None,
) -> str:
    terms = glossary_terms or DEFAULT_GLOSSARY_TERMS

    prompt = (
        "This is a Russian business and IT meeting. "
        "Most speech is Russian, but speakers frequently use English product, UI, technical, "
        "and project-management terms. "
        "If a word does not sound like a valid Russian word, prefer preserving it as a likely "
        "English IT or product term instead of inventing a Russian-looking word. "
        "Do not translate product names or domain terms into Russian. "
        "Important terms: "
        + ", ".join(terms)
        + "."
    )

    if previous_text:
        prompt += "\nPrevious context: " + previous_text[-700:]

    return prompt


def update_previous_context(
    previous_text: str,
    current_text: str,
    max_chars: int = 1200,
) -> str:
    combined = (previous_text + "\n" + (current_text or "")).strip()
    return combined[-max_chars:]
