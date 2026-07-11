import json

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class ProjectRepository:
    def __init__(self):
        init_fact_schema()

    def get_latest_summary(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_summary ORDER BY updated_at DESC, id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def save_summary(self, summary: str, title: str = "Project Summary", metadata: dict | None = None):
        latest = self.get_latest_summary()
        version = int(latest["version"]) + 1 if latest else 1
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO project_summary (title, summary, metadata_json, version) VALUES (?, ?, ?, ?)",
            (title, summary, json.dumps(metadata or {}, ensure_ascii=False), version),
        )
        summary_id = cur.lastrowid
        conn.commit()
        conn.close()
        return summary_id

    def list_summaries(self, limit: int = 20):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_summary ORDER BY updated_at DESC, id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_model_statistics(self):
        conn = get_connection()
        cur = conn.cursor()
        stats = {}

        for table_name in [
            "facts", "entities", "entity_relationships", "entity_ontology",
            "domain_objects", "actors", "processes", "knowledge", "documents", "chunks",
        ]:
            try:
                cur.execute(f"SELECT COUNT(*) AS count FROM {table_name}")
                stats[table_name] = cur.fetchone()["count"]
            except Exception:
                stats[table_name] = 0

        grouped_queries = {
            "facts_by_type": "SELECT fact_type AS type, COUNT(*) AS count FROM facts GROUP BY fact_type ORDER BY count DESC",
            "ontology_by_type": "SELECT ontology_type AS type, COUNT(*) AS count FROM entity_ontology GROUP BY ontology_type ORDER BY count DESC",
            "domain_objects_by_type": "SELECT object_type AS type, COUNT(*) AS count FROM domain_objects GROUP BY object_type ORDER BY count DESC",
            "actors_by_type": "SELECT actor_type AS type, COUNT(*) AS count FROM actors GROUP BY actor_type ORDER BY count DESC",
            "processes_by_type": "SELECT process_type AS type, COUNT(*) AS count FROM processes GROUP BY process_type ORDER BY count DESC",
            "relationships_by_predicate": "SELECT predicate AS type, COUNT(*) AS count FROM entity_relationships GROUP BY predicate ORDER BY count DESC LIMIT 50",
        }

        for key, sql in grouped_queries.items():
            try:
                cur.execute(sql)
                stats[key] = [dict(row) for row in cur.fetchall()]
            except Exception:
                stats[key] = []

        conn.close()
        return stats

