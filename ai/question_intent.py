def classify_question_intent(question: str) -> dict:
    """
    Lightweight deterministic intent classifier for Project Brain AI Analyst.

    The most important fix here is to classify broad overview questions correctly.
    Previously short questions like "о чем проект вкратце" could fall through to
    general/entity retrieval and the answer was dominated by a random transcript chunk.
    """
    q = (question or "").lower().strip()

    overview_markers = [
        "о чем проект", "о чём проект", "о чем система", "о чём система",
        "суть проекта", "суть системы", "что это за проект", "что это за система",
        "опиши проект", "опиши систему", "кратко проект", "вкратце", "коротко",
        "project about", "system about", "describe the project", "describe the system",
        "what is this project", "what is this system", "overview", "summary",
        "short overview", "briefly", "in short",
    ]

    requirements_markers = [
        "требован", "requirements", "requirement", "acceptance criteria",
        "ac ", "user story", "stories",
    ]

    risk_markers = [
        "риск", "риски", "risk", "risks", "constraint", "ограничен",
        "проблем", "issue", "blocker", "bug",
    ]

    question_markers = [
        "открытые вопросы", "open questions", "что неизвестно",
        "непонятно", "gaps", "missing", "unknown", "что нужно уточнить",
    ]

    integration_markers = [
        "интеграц", "integration", "api", "endpoint", "webhook",
        "external", "service", "swagger",
    ]

    process_markers = [
        "процесс", "process", "workflow", "flow", "как проходит",
        "lifecycle", "жизненный цикл", "пайплайн", "этапы", "стадии",
    ]

    actor_markers = [
        "акторы", "участники", "роли", "кто участвует", "actors", "roles",
        "participants", "responsibilities", "кто отвечает",
    ]

    relationship_markers = [
        "связан", "связи", "depends", "depend", "зависит", "кто утверждает",
        "who approves", "connected", "relationship", "graph",
    ]

    decision_markers = [
        "решени", "decision", "decisions", "почему решили", "why decided",
    ]

    entity_markers = [
        "merchant", "advance", "funder", "underwriter", "worksheet",
        "funding", "underwriting", "payment", "payback", "syndicator",
        "isa", "iso", "loc", "loci", "rdmetr", "plaid", "stripe",
    ]

    def has_any(markers):
        return any(marker in q for marker in markers)

    # Overview must be checked first. It intentionally wins over entity words like
    # "project" or short vague terms.
    if has_any(overview_markers):
        intent = "project_overview"
    elif has_any(requirements_markers):
        intent = "requirements"
    elif has_any(risk_markers):
        intent = "risks"
    elif has_any(question_markers):
        intent = "open_questions"
    elif has_any(integration_markers):
        intent = "integrations"
    elif has_any(actor_markers):
        intent = "actors"
    elif has_any(process_markers):
        intent = "processes"
    elif has_any(relationship_markers):
        intent = "relationships"
    elif has_any(decision_markers):
        intent = "decisions"
    elif has_any(entity_markers):
        intent = "entity_deep_dive"
    else:
        intent = "general"

    entities = []
    known_entities = [
        "Merchant", "Advance", "Funder", "Underwriter", "Worksheet", "Funding",
        "Underwriting", "Payment", "Payback", "Syndicator", "ISA", "ISO", "LoCi",
        "RDMetr", "Plaid", "Stripe", "Confluence", "Jira", "Slack",
    ]

    for entity in known_entities:
        if entity.lower() in q:
            entities.append(entity)

    return {
        "intent": intent,
        "entities": entities,
        "raw_question": question,
    }

