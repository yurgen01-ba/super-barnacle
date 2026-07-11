from collections import defaultdict

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_REPORT_MODEL


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _compact_memory(memory_items, max_items_per_type=18):
    grouped = defaultdict(list)

    for item in memory_items:
        grouped[item.get("type", "unknown")].append(item)

    priority_order = [
        "feature",
        "requirement",
        "business_rule",
        "decision",
        "integration",
        "risk",
        "question",
        "assumption",
        "glossary",
    ]

    lines = []

    for item_type in priority_order:
        items = grouped.get(item_type, [])[:max_items_per_type]

        if not items:
            continue

        lines.append(f"\n## {item_type.upper()}")

        for item in items:
            title = (item.get("title") or "")[:180]
            content = (item.get("content") or "")[:650]
            source = item.get("source", "unknown")
            lines.append(f"- {title}: {content} (source: {source})")

    return "\n".join(lines).strip()


def generate_confluence_article(
    memory_items,
    article_type: str = "project_overview",
    article_title: str = "",
    audience: str = "business_analyst",
    additional_instructions: str = "",
):
    if not memory_items:
        return ""

    compact_memory = _compact_memory(memory_items)

    if not compact_memory:
        return ""

    article_type_instruction = {
        "project_overview": "Create a Project Overview article for onboarding.",
        "functional_spec": "Create a Functional Specification article with requirements and business rules.",
        "technical_overview": "Create a Technical/System Overview article focused on services, integrations, data flows, and dependencies.",
        "decision_log": "Create a Decision Log article summarizing key decisions, context, and consequences.",
        "risk_register": "Create a Risk Register article with risks, impact, mitigation, and open questions.",
        "onboarding": "Create an Onboarding Guide for a new analyst or developer joining the project.",
    }.get(article_type, "Create a useful Confluence article.")

    audience_instruction = {
        "business_analyst": "Audience: Business Analyst. Emphasize domain, requirements, business rules, open questions.",
        "system_analyst": "Audience: System Analyst. Emphasize integrations, system behavior, APIs, data, edge cases.",
        "developer": "Audience: Developer. Emphasize implementation-relevant details, services, dependencies, risks.",
        "product_manager": "Audience: Product Manager. Emphasize product scope, decisions, risks, open questions.",
        "qa": "Audience: QA. Emphasize acceptance criteria, business rules, risks, edge cases.",
        "mixed": "Audience: mixed project team. Keep balance between business and technical context.",
    }.get(audience, "Audience: mixed project team.")

    prompt = f"""
You are a senior Business/System Analyst writing a Confluence article from Project Memory.

{article_type_instruction}
{audience_instruction}

Return Markdown only.
Do NOT return JSON.
Do NOT wrap output in code fences.

Rules:
- Use ONLY provided Project Memory.
- Do not invent details.
- If information is missing, write "Not found in provided sources".
- Do not merely retell every source item.
- Synthesize into a useful Confluence article.
- Use clear headings.
- Use tables where helpful.
- Include source references briefly in relevant sections.
- Add an "Open Questions" section if there are questions or missing facts.
- Add a "Source Basis" section at the end.
- Keep the article practical and ready to paste into Confluence.

Article title:
{article_title or "Project Knowledge Article"}

Additional instructions:
{additional_instructions or "None"}

PROJECT MEMORY:
{compact_memory}
"""

    response = client.messages.create(
        model=CLAUDE_REPORT_MODEL,
        max_tokens=4500,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()

