from __future__ import annotations

from ui.artifacts.artifact_framework import render_artifact_framework
from ui.extraction_report import render_extraction_report


def render_artifact_framework_v2(project_id: str = "default"):
    render_artifact_framework(project_id=project_id)


def render_extraction_report_v2(extraction: dict):
    render_extraction_report(extraction)
