from __future__ import annotations
from pathlib import Path
from repositories.artifact_repository import artifact_repository

class ArtifactDownloadManager:
    def export_artifact(self, artifact: dict, output_dir: str | Path = "exports/artifacts") -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".md" if artifact.get("format") == "markdown" else ".txt"
        safe_title = "".join(ch if ch.isalnum() else "_" for ch in artifact.get("title","artifact"))[:80]
        path = output_dir / f"{artifact['artifact_type']}_{safe_title}_{artifact['id'][:8]}{suffix}"
        path.write_text(artifact.get("content") or "", encoding="utf-8")
        return path

artifact_download_manager = ArtifactDownloadManager()
