from __future__ import annotations

from uuid import uuid4

from services.artifact_service import artifact_service


USER_ARTIFACT_ORIGIN = "user_ai_request"


def save_user_generated_artifact(
    *,
    project_id: str,
    artifact_type: str,
    title: str,
    content: str,
    description: str = "",
    format: str = "markdown",
    metadata: dict | None = None,
):
    """Persist a delivery-ready artifact explicitly requested by the user."""
    artifact_metadata = {
        **(metadata or {}),
        "origin": USER_ARTIFACT_ORIGIN,
        "requested_by": "user",
        "generated_by": "ai",
    }
    return artifact_service.save_artifact(
        extraction_id=f"user-ai-{uuid4()}",
        project_id=project_id,
        artifact_type=artifact_type,
        title=title,
        content=content,
        description=description,
        format=format,
        metadata=artifact_metadata,
    )
