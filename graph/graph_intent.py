from __future__ import annotations


class GraphIntent:
    PROJECT_OVERVIEW = "project_overview"
    ACTORS = "actors"
    PROCESSES = "processes"
    ENTITIES = "entities"
    RULES = "rules"
    UNKNOWN = "unknown"


OVERVIEW_PATTERNS = [
    "опиши проект",
    "о чем проект",
    "суть проекта",
    "кратко проект",
    "project overview",
    "describe project",
    "what is the project",
]


def detect_graph_intent(question: str) -> str:
    q = (question or "").lower().strip()

    if any(pattern in q for pattern in OVERVIEW_PATTERNS):
        return GraphIntent.PROJECT_OVERVIEW

    if "актор" in q or "actor" in q or "участник" in q:
        return GraphIntent.ACTORS

    if "процесс" in q or "process" in q:
        return GraphIntent.PROCESSES

    if "сущност" in q or "entity" in q or "entities" in q:
        return GraphIntent.ENTITIES

    if "правил" in q or "rule" in q:
        return GraphIntent.RULES

    return GraphIntent.UNKNOWN
