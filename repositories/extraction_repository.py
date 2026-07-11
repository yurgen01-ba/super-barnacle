from __future__ import annotations
import json, sqlite3
from pathlib import Path
from models.extraction import Extraction

class ExtractionRepository:
    def __init__(self, db_path: str | Path = "data/extractions.db"):
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self._ensure_schema()
    def _connect(self): return sqlite3.connect(self.db_path)
    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS extractions(
                id TEXT PRIMARY KEY, project_id TEXT, source_id TEXT, source_name TEXT, source_type TEXT,
                status TEXT, started_at TEXT, finished_at TEXT, duration_seconds REAL, artifact_count INTEGER,
                statistics_json TEXT, metadata_json TEXT)""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_extractions_project ON extractions(project_id)")
    def save(self, extraction: Extraction) -> Extraction:
        d = extraction.to_dict()
        with self._connect() as conn:
            conn.execute("""INSERT OR REPLACE INTO extractions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (d["id"], d["project_id"], d["source_id"], d["source_name"], d["source_type"], d["status"], d["started_at"],
                 d["finished_at"], d["duration_seconds"], d["artifact_count"], json.dumps(d["statistics"], ensure_ascii=False),
                 json.dumps(d["metadata"], ensure_ascii=False)))
        return extraction
    def list(self, project_id: str = "default", limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM extractions WHERE project_id=? ORDER BY started_at DESC LIMIT ?", (project_id, limit)).fetchall()
        keys = ["id","project_id","source_id","source_name","source_type","status","started_at","finished_at","duration_seconds","artifact_count","statistics_json","metadata_json"]
        result=[]
        for row in rows:
            d=dict(zip(keys,row)); d["statistics"]=json.loads(d.pop("statistics_json") or "{}"); d["metadata"]=json.loads(d.pop("metadata_json") or "{}"); result.append(d)
        return result

extraction_repository = ExtractionRepository()
