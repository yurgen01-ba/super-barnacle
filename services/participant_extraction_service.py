from __future__ import annotations

import re

from repositories.participant_repository import participant_repository


SLACK_NAME_RE = re.compile(
    r"^(?:\[[^\]]+\]\s*)?([A-ZА-ЯІЇЄ][\w'’.-]+(?:\s+[A-ZА-ЯІЇЄ][\w'’.-]+){0,2})\s*:",
    re.MULTILINE,
)
LABELED_NAME_RE = re.compile(
    r"(?im)^\s*(assignee|reporter|author|owner|creator|исполнитель|автор|владелец|ответственный)\s*[:：]\s*([^\n,;]{2,120})"
)


def extract_participants_from_text(
    *,
    text: str,
    source_type: str,
    source_ref: str,
    project_id: str,
) -> int:
    found: dict[str, str | None] = {}
    if source_type == "slack":
        for match in SLACK_NAME_RE.finditer(text or ""):
            found[match.group(1).strip()] = None
    for match in LABELED_NAME_RE.finditer(text or ""):
        found[match.group(2).strip()] = match.group(1).strip()
    for name, role in found.items():
        participant_repository.upsert(
            project_id=project_id,
            name=name,
            source_type=source_type,
            source_ref=source_ref,
            role=role,
        )
    return len(found)


def save_manual_participants(
    *,
    names: list[str],
    project_id: str,
    source_ref: str,
) -> None:
    for index, name in enumerate(names):
        participant_repository.upsert(
            project_id=project_id,
            name=name,
            source_type="meeting",
            source_ref=source_ref,
            role=f"SPEAKER_{index:02d}",
        )
