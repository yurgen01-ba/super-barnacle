from __future__ import annotations
import json, sqlite3
from pathlib import Path
from models.artifact import KnowledgeArtifact

class ArtifactRepository:
    def __init__(self, db_path: str | Path = "data/artifacts.db"):
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self._ensure_schema()
    def _connect(self): return sqlite3.connect(self.db_path)
    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS artifacts(
                id TEXT PRIMARY KEY, extraction_id TEXT, project_id TEXT, artifact_type TEXT, title TEXT,
                description TEXT, content TEXT, format TEXT, status TEXT, created_at TEXT, metadata_json TEXT)""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_extraction ON artifacts(extraction_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_id)")
    def save(self, artifact: KnowledgeArtifact) -> KnowledgeArtifact:
        d = artifact.to_dict()
        with self._connect() as conn:
            conn.execute("""INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (d["id"], d["extraction_id"], d["project_id"], d["artifact_type"], d["title"], d["description"], d["content"], d["format"], d["status"], d["created_at"], json.dumps(d["metadata"], ensure_ascii=False)))
        return artifact
    def list_by_extraction(self, extraction_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM artifacts WHERE extraction_id=? ORDER BY created_at ASC", (extraction_id,)).fetchall()
        keys=["id","extraction_id","project_id","artifact_type","title","description","content","format","status","created_at","metadata_json"]
        result=[]
        for row in rows:
            d=dict(zip(keys,row)); d["metadata"]=json.loads(d.pop("metadata_json") or "{}"); result.append(d)
        return result

artifact_repository = ArtifactRepository()
