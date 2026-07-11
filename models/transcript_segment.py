from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class TranscriptSegment:
    id: str
    project_id: str
    source: str
    file_name: str
    segment_no: int
    total_segments: int
    text: str
    text_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        source: str,
        file_name: str,
        segment_no: int,
        total_segments: int,
        text: str,
        project_id: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> "TranscriptSegment":
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            source=source,
            file_name=file_name,
            segment_no=segment_no,
            total_segments=total_segments,
            text=text,
            text_hash=sha256(text.encode("utf-8", errors="ignore")).hexdigest(),
            metadata=metadata or {},
        )
