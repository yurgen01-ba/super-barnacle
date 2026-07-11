from collections import defaultdict

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_REPORT_MODEL


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _compact_memory(memory_items, max_items_per_type=8):
    grouped = defaultdict(list)

    for item in memory_items:
        grouped[item.get("type", "unknown")].append(item)

    priority_order = [
        "feature",
        "requirement",
        "business_rule",
        "decision",
        "risk",
        "question",
        "integration",
        "glossary",
        "assumption",
    ]

    lines = []

    for item_type in priority_order:
        items = grouped.get(item_type, [])[:max_items_per_type]

        if not items:
            continue

        lines.append(f"\n## {item_type.upper()}")

        for item in items:
            title = (item.get("title") or "")[:160]
            content = (item.get("content") or "")[:350]
            source = item.get("source", "unknown")
            lines.append(f"- {title}: {content} (source: {source})")

    return "\n".join(lines).strip()


def generate_project_report(memory_items, mode="executive"):
    if not memory_items:
        return "Project Memory is empty. Add Slack, Jira, or Meeting data first."

    max_items = 8 if mode == "executive" else 15
    compact_memory = _compact_memory(memory_items, max_items_per_type=max_items)

    if not compact_memory:
        return "Project Memory does not contain enough concrete information to generate a useful summary."

    if mode == "executive":
        prompt = f"""
You are a senior product/business analyst.

Create a SHORT project summary from Project Memory.

Rules:
- Do NOT retell source files.
- Do NOT list every ticket.
- Do NOT produce a long report.
- Use ONLY provided Project Memory.
- If something is missing, say "Not found in provided sources".
- Keep the answer concise.

Output format:
1. Project in 3-5 lines
2. What the system/product does
3. Main functional areas
4. Key decisions
5. Main risks/blockers
6. Open questions
7. Recommended next 3 analyst actions

Maximum length: 350-500 words.

PROJECT MEMORY:
{compact_memory}
"""
        max_tokens = 900
    else:
        prompt = f"""
You are a senior business/system analyst.

Create a concise analyst-oriented project report from Project Memory.

Rules:
- Do NOT retell all source files.
- Focus on synthesis.
- Use ONLY provided Project Memory.
- Reference sources briefly.
- Keep it structured but not verbose.

Sections:
1. Project overview
2. Core business capabilities
3. Requirements and rules
4. Decisions
5. Risks and blockers
6. Open questions
7. Next analyst steps

Maximum length: 900-1200 words.

PROJECT MEMORY:
{compact_memory}
"""
        max_tokens = 1800

    response = client.messages.create(
        model=CLAUDE_REPORT_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text

