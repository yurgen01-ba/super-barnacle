from collections import defaultdict

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_REPORT_MODEL


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _compact_memory_for_tickets(memory_items, max_items_per_type=18):
    grouped = defaultdict(list)

    for item in memory_items:
        grouped[item.get("type", "unknown")].append(item)

    priority_order = [
        "requirement",
        "feature",
        "business_rule",
        "risk",
        "question",
        "decision",
        "integration",
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


def generate_jira_ticket_drafts_markdown(
    memory_items,
    project_context: str = "",
    ticket_style: str = "mixed",
    granularity: str = "balanced",
):
    """
    Generate Jira-ready ticket drafts as Markdown.

    AI decides the number of tickets based on logical scope boundaries.
    """
    if not memory_items:
        return ""

    compact_memory = _compact_memory_for_tickets(memory_items)

    if not compact_memory:
        return ""

    style_instruction = {
        "user_story": "Prefer Jira Stories written as user stories where appropriate.",
        "technical_task": "Prefer Jira Technical Tasks focused on backend/system implementation.",
        "bug": "Create Jira Bugs only where clear defects/problems are visible.",
        "mixed": "Create a practical mix of Stories, Tasks, Bugs, and Spikes.",
    }.get(ticket_style, "Create a practical mix of Stories, Tasks, Bugs, and Spikes.")

    granularity_instruction = {
        "coarse": (
            "Use coarse granularity: fewer, larger tickets. "
            "Group closely related requirements into a single ticket when they share the same user goal or technical component."
        ),
        "balanced": (
            "Use balanced granularity: split tickets by logical scope, user value, dependency, and implementability. "
            "Avoid both huge epics and tiny micro-tasks."
        ),
        "fine": (
            "Use fine granularity: create smaller implementation-ready tickets. "
            "Split by component, scenario, edge case, or acceptance criteria when useful."
        ),
    }.get(granularity, "Use balanced granularity.")

    prompt = f"""
You are a senior Business/System Analyst creating Jira ticket drafts from Project Memory.

Goal:
Create actionable Jira-ready tickets based ONLY on the provided Project Memory.

Ticket style:
{style_instruction}

Ticket splitting:
{granularity_instruction}

IMPORTANT:
You decide the number of tickets.
Do NOT force a fixed ticket count.
Create as many tickets as logically needed, but avoid duplicates and avoid over-splitting.
A good output usually has 3-12 tickets depending on the available information.

How to split logically:
- Split by independent user goal.
- Split by system component/service.
- Split by dependency or integration boundary.
- Split by implementation sequence when one part blocks another.
- Split bugs separately from new requirements.
- Use Spike when the next action is investigation/clarification.
- Do not create one ticket per memory item.
- Do not merge unrelated requirements into one huge ticket.
- If the Project Memory is too generic, create fewer tickets and add Notes for BA.

Return Markdown only.
Do NOT return JSON.
Do NOT wrap output in markdown code fences.

For each ticket use this exact structure:

## Ticket N: <summary>

**Issue type:** Story | Task | Bug | Spike  
**Priority:** Highest | High | Medium | Low  
**Labels:** label-1, label-2

### Description
<clear Jira description>

### Acceptance Criteria
- <criterion 1>
- <criterion 2>
- <criterion 3>

### Source Basis
- <source or memory item that supports this ticket>

### Notes for BA
<what should be clarified before implementation, or "None">

Rules:
- Do NOT invent unsupported features.
- Use only facts from Project Memory.
- If an item is unclear, create a Spike or add clarification in Notes for BA.
- Prefer actionable tickets over broad epics.
- Include acceptance criteria for every Story/Task/Bug.
- Keep tickets concise but implementation-ready.

Project context:
{project_context or "Not provided"}

PROJECT MEMORY:
{compact_memory}
"""

    response = client.messages.create(
        model=CLAUDE_REPORT_MODEL,
        max_tokens=4500,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()


def generate_jira_ticket_drafts(
    memory_items,
    project_context: str = "",
    ticket_style: str = "mixed",
    granularity: str = "balanced",
):
    return generate_jira_ticket_drafts_markdown(
        memory_items=memory_items,
        project_context=project_context,
        ticket_style=ticket_style,
        granularity=granularity,
    )

