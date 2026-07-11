from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ArtifactTypeMeta:
    type_id: str
    title: str
    category: str
    icon: str
    order: int
    default_format: str = "markdown"
    description: str = ""

ARTIFACT_TYPES = {
    "transcript": ArtifactTypeMeta("transcript", "Transcript", "human", "📝", 10, "markdown", "Full meeting transcript."),
    "clean_transcript": ArtifactTypeMeta("clean_transcript", "Clean Transcript", "human", "✨", 20, "markdown", "Cleaned transcript."),
    "repaired_transcript": ArtifactTypeMeta("repaired_transcript", "Repaired Transcript", "human", "🛠️", 25, "markdown", "Transcript repaired with glossary and quality layer."),
    "transcript_quality": ArtifactTypeMeta("transcript_quality", "Transcript Quality", "developer", "📈", 26, "json", "Transcript quality diagnostics."),
    "screen_timeline": ArtifactTypeMeta("screen_timeline", "Screen Timeline", "human", "📷", 30, "json", "Screen analysis timeline."),
    "knowledge": ArtifactTypeMeta("knowledge", "Extracted Knowledge", "knowledge", "🧠", 40, "json", "Accepted extracted facts."),
    "rejected_facts": ArtifactTypeMeta("rejected_facts", "Rejected Facts", "knowledge", "❌", 50, "json", "Rejected facts and reasons."),
    "ontology_mapping": ArtifactTypeMeta("ontology_mapping", "Ontology Mapping", "knowledge", "🔗", 60, "json", "Canonical ontology mapping."),
    "project_model": ArtifactTypeMeta("project_model", "Project Model", "knowledge", "📊", 70, "json", "Project model snapshot."),
    "project_summary": ArtifactTypeMeta("project_summary", "Project Summary", "knowledge", "📄", 80, "markdown", "Project summary."),
    "summary_diff": ArtifactTypeMeta("summary_diff", "Summary Diff", "knowledge", "🧾", 90, "markdown", "Extraction diff."),
    "reasoning_context": ArtifactTypeMeta("reasoning_context", "Reasoning Context", "developer", "🧩", 100, "markdown", "Reasoning context."),
    "prompt": ArtifactTypeMeta("prompt", "Prompt", "developer", "🤖", 110, "markdown", "Final model prompt."),
    "final_answer": ArtifactTypeMeta("final_answer", "Final Answer", "developer", "💬", 120, "markdown", "Final answer."),
    "logs": ArtifactTypeMeta("logs", "Logs", "developer", "🪵", 130, "json", "Processing logs."),
}
def get_artifact_meta(type_id: str) -> ArtifactTypeMeta:
    return ARTIFACT_TYPES.get(type_id, ArtifactTypeMeta(type_id, type_id.replace("_", " ").title(), "other", "📦", 999, "text", "Generated artifact."))
def sort_artifacts(artifacts: list[dict]) -> list[dict]:
    return sorted(artifacts, key=lambda a: get_artifact_meta(a.get("artifact_type", "")).order)
def group_artifacts(artifacts: list[dict]) -> dict[str, list[dict]]:
    grouped = {}
    for artifact in sort_artifacts(artifacts):
        grouped.setdefault(get_artifact_meta(artifact.get("artifact_type", "")).category, []).append(artifact)
    return grouped
