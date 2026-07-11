from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any
from uuid import uuid4

@dataclass(slots=True)
class ProjectModelItem:
    id: str
    item_type: str
    canonical_name: str
    display_name: str
    description: str = ""
    confidence: float = 0.7
    status: str = "active"
    source_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, item_type: str, canonical_name: str, display_name: str | None = None, description: str = "", confidence: float = 0.7, source_ids: list[str] | None = None, evidence_ids: list[str] | None = None, metadata: dict[str, Any] | None = None):
        return cls(id=f"{item_type}:{canonical_name.lower().replace(' ', '_')}:{uuid4().hex[:8]}", item_type=item_type, canonical_name=canonical_name, display_name=display_name or canonical_name, description=description, confidence=confidence, source_ids=source_ids or [], evidence_ids=evidence_ids or [], metadata=metadata or {})

@dataclass(slots=True)
class ProjectModel:
    project_id: str
    domain: str = ""
    description: str = ""
    actors: list[ProjectModelItem] = field(default_factory=list)
    processes: list[ProjectModelItem] = field(default_factory=list)
    entities: list[ProjectModelItem] = field(default_factory=list)
    business_rules: list[ProjectModelItem] = field(default_factory=list)
    requirements: list[ProjectModelItem] = field(default_factory=list)
    decisions: list[ProjectModelItem] = field(default_factory=list)
    integrations: list[ProjectModelItem] = field(default_factory=list)
    risks: list[ProjectModelItem] = field(default_factory=list)
    open_questions: list[ProjectModelItem] = field(default_factory=list)
    version: int = 1
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def all_items(self) -> list[ProjectModelItem]:
        return self.actors + self.processes + self.entities + self.business_rules + self.requirements + self.decisions + self.integrations + self.risks + self.open_questions

    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id, "domain": self.domain, "description": self.description, "actors": [asdict(x) for x in self.actors], "processes": [asdict(x) for x in self.processes], "entities": [asdict(x) for x in self.entities], "business_rules": [asdict(x) for x in self.business_rules], "requirements": [asdict(x) for x in self.requirements], "decisions": [asdict(x) for x in self.decisions], "integrations": [asdict(x) for x in self.integrations], "risks": [asdict(x) for x in self.risks], "open_questions": [asdict(x) for x in self.open_questions], "version": self.version, "updated_at": self.updated_at.isoformat(), "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        def items(key): return [ProjectModelItem(**x) for x in data.get(key, []) or []]
        return cls(project_id=data.get("project_id", "default"), domain=data.get("domain", ""), description=data.get("description", ""), actors=items("actors"), processes=items("processes"), entities=items("entities"), business_rules=items("business_rules"), requirements=items("requirements"), decisions=items("decisions"), integrations=items("integrations"), risks=items("risks"), open_questions=items("open_questions"), version=int(data.get("version") or 1), metadata=data.get("metadata") or {})
