from __future__ import annotations
import json, sqlite3
from pathlib import Path
from models.knowledge_provenance import ProvenanceRecord
class KnowledgeProvenanceRepository:
    def __init__(self, db_path='data/knowledge_provenance.db'):
        self.db_path=Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self._ensure_schema()
    def _connect(self): return sqlite3.connect(self.db_path)
    def _ensure_schema(self):
        with self._connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS provenance_records(id TEXT PRIMARY KEY, project_id TEXT, source_id TEXT, source_type TEXT, artifact_type TEXT, title TEXT, content TEXT, stage TEXT, created_at TEXT, metadata_json TEXT)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_prov_project ON provenance_records(project_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_prov_source ON provenance_records(source_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_prov_type ON provenance_records(artifact_type)')
    def save(self, r: ProvenanceRecord):
        with self._connect() as c:
            c.execute('INSERT OR REPLACE INTO provenance_records VALUES (?,?,?,?,?,?,?,?,?,?)',(r.id,r.project_id,r.source_id,r.source_type,r.artifact_type,r.title,r.content,r.stage,r.created_at.isoformat(),json.dumps(r.metadata,ensure_ascii=False)))
        return r
    def create(self, source_id, source_type, artifact_type, title, content, stage, project_id='default', metadata=None):
        return self.save(ProvenanceRecord.create(source_id,source_type,artifact_type,title,content,stage,project_id,metadata))
    def list_records(self, project_id='default', source_id=None, artifact_type=None, limit=200):
        q='SELECT * FROM provenance_records WHERE project_id=?'; p=[project_id]
        if source_id: q+=' AND source_id=?'; p.append(source_id)
        if artifact_type: q+=' AND artifact_type=?'; p.append(artifact_type)
        q+=' ORDER BY created_at DESC LIMIT ?'; p.append(limit)
        with self._connect() as c: rows=c.execute(q,p).fetchall()
        return [{'id':r[0],'project_id':r[1],'source_id':r[2],'source_type':r[3],'artifact_type':r[4],'title':r[5],'content':r[6] or '','stage':r[7],'created_at':r[8],'metadata':json.loads(r[9] or '{}')} for r in rows]
knowledge_provenance_repository=KnowledgeProvenanceRepository()
