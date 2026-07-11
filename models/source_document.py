from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class SourceDocument:
    id: str
    project_id: str
    source_type: str
    title: str
    original_text: str
    source_ref: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        source_type: str,
        title: str,
        original_text: str,
        project_id: str = "default",
        source_ref: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "SourceDocument":
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            source_type=source_type,
            title=title,
            original_text=original_text,
            source_ref=source_ref,
            metadata=metadata or {},
        )

    def text_hash(self) -> str:
        return sha256(self.original_text.encode("utf-8", errors="ignore")).hexdigest()


@dataclass(slots=True)
class SourceChunk:
    id: str
    document_id: str
    project_id: str
    chunk_no: int
    text: str
    text_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        document_id: str,
        project_id: str,
        chunk_no: int,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> "SourceChunk":
        return cls(
            id=str(uuid4()),
            document_id=document_id,
            project_id=project_id,
            chunk_no=chunk_no,
            text=text,
            text_hash=sha256(text.encode("utf-8", errors="ignore")).hexdigest(),
            metadata=metadata or {},
        )
