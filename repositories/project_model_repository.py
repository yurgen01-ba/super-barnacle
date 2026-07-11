from __future__ import annotations
import json, sqlite3
from pathlib import Path
from models.project_model import ProjectModel

class ProjectModelRepository:
    def __init__(self, db_path: str | Path = "data/project_model.db"):
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self._ensure_schema()
    def _connect(self): return sqlite3.connect(self.db_path)
    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS project_models (project_id TEXT PRIMARY KEY, version INTEGER NOT NULL, payload_json TEXT NOT NULL, updated_at TEXT NOT NULL)""")
    def get(self, project_id: str = "default") -> ProjectModel | None:
        with self._connect() as conn: row = conn.execute("SELECT payload_json FROM project_models WHERE project_id=?", (project_id,)).fetchone()
        return ProjectModel.from_dict(json.loads(row[0])) if row else None
    def save(self, model: ProjectModel) -> ProjectModel:
        payload=model.to_dict()
        with self._connect() as conn:
            conn.execute("INSERT OR REPLACE INTO project_models(project_id, version, payload_json, updated_at) VALUES (?,?,?,?)", (model.project_id, model.version, json.dumps(payload, ensure_ascii=False), payload["updated_at"]))
        return model
    def get_or_create(self, project_id: str = "default") -> ProjectModel:
        existing=self.get(project_id)
        if existing: return existing
        model=ProjectModel(project_id=project_id, domain="Merchant Cash Advance / credit operations", description="OrgMeter is a platform for managing MCA-style credits / Advances, merchants, funders, partners, underwriting, payback allocation, fees, payout history, reporting and integrations.")
        return self.save(model)
project_model_repository=ProjectModelRepository()
