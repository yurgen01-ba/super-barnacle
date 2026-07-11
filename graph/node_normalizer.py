from __future__ import annotations

from typing import Any

from models.knowledge_node import KnowledgeNode


FIELD_CANDIDATES = {
    "id": ["id", "uuid", "key", "code", "name", "title"],
    "title": ["title", "name", "label", "summary", "key", "type"],
    "description": ["description", "content", "text", "details", "summary", "value"],
    "confidence": ["confidence", "score"],
    "status": ["status", "state"],
}


def get_value(item: Any, names: list[str], default: Any = "") -> Any:
    if item is None:
        return default

    if isinstance(item, dict):
        for name in names:
            value = item.get(name)
            if value not in (None, ""):
                return value
        return default

    for name in names:
        value = getattr(item, name, None)
        if value not in (None, ""):
            return value

    return default


def slug(value: Any) -> str:
    text = str(value or "").strip().lower()
    safe = "".join(ch if ch.isalnum() else "_" for ch in text)
    safe = "_".join(part for part in safe.split("_") if part)
    return safe or "unknown"


def normalize_to_node(
    item: Any,
    node_type: str,
    source: str,
    fallback_index: int,
) -> KnowledgeNode:
    raw_id = get_value(item, FIELD_CANDIDATES["id"], fallback_index)
    title = get_value(item, FIELD_CANDIDATES["title"], f"{node_type} {fallback_index}")
    description = get_value(item, FIELD_CANDIDATES["description"], "")

    confidence = get_value(item, FIELD_CANDIDATES["confidence"], 0.7)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.7

    status = str(get_value(item, FIELD_CANDIDATES["status"], "active") or "active")

    return KnowledgeNode(
        id=f"{node_type}:{slug(raw_id)}",
        node_type=node_type,
        title=str(title),
        description=str(description or ""),
        confidence=confidence,
        status=status,
        source=source,
        source_id=str(raw_id),
        metadata={
            "raw_type": type(item).__name__,
            "raw_id": str(raw_id),
        },
    )
