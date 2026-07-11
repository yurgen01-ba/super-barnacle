import json

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class ActorsRepository:
    def __init__(self):
        init_fact_schema()

    def upsert_actor(
        self,
        entity_id: int,
        name: str,
        actor_type: str = "unknown",
        description: str | None = None,
        responsibilities: list[dict] | None = None,
        owned_objects: list[dict] | None = None,
        participates_in: list[dict] | None = None,
        interactions: list[dict] | None = None,
        permissions: list[dict] | None = None,
        evidence: list[dict] | None = None,
        confidence: float = 0.7,
    ):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO actors (
                entity_id, name, actor_type, description,
                responsibilities_json, owned_objects_json, participates_in_json,
                interactions_json, permissions_json, evidence_json, confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_id) DO UPDATE SET
                name = excluded.name,
                actor_type = excluded.actor_type,
                description = excluded.description,
                responsibilities_json = excluded.responsibilities_json,
                owned_objects_json = excluded.owned_objects_json,
                participates_in_json = excluded.participates_in_json,
                interactions_json = excluded.interactions_json,
                permissions_json = excluded.permissions_json,
                evidence_json = excluded.evidence_json,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                entity_id,
                name,
                actor_type,
                description,
                json.dumps(responsibilities or [], ensure_ascii=False),
                json.dumps(owned_objects or [], ensure_ascii=False),
                json.dumps(participates_in or [], ensure_ascii=False),
                json.dumps(interactions or [], ensure_ascii=False),
                json.dumps(permissions or [], ensure_ascii=False),
                json.dumps(evidence or [], ensure_ascii=False),
                confidence,
            ),
        )

        conn.commit()
        conn.close()

    def list_actors(self, limit: int = 300):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT a.*, e.entity_type, eo.ontology_type
            FROM actors a
            JOIN entities e ON e.id = a.entity_id
            LEFT JOIN entity_ontology eo ON eo.entity_id = e.id
            ORDER BY a.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cur.fetchall()
        conn.close()
        return [self._decode_row(dict(row)) for row in rows]

    def search_actors(self, query: str, limit: int = 300):
        query = (query or "").strip()
        if not query:
            return self.list_actors(limit=limit)

        like = f"%{query}%"
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT a.*, e.entity_type, eo.ontology_type
            FROM actors a
            JOIN entities e ON e.id = a.entity_id
            LEFT JOIN entity_ontology eo ON eo.entity_id = e.id
            WHERE a.name LIKE ?
               OR a.actor_type LIKE ?
               OR a.description LIKE ?
               OR a.responsibilities_json LIKE ?
               OR a.owned_objects_json LIKE ?
               OR a.participates_in_json LIKE ?
               OR a.interactions_json LIKE ?
            ORDER BY a.confidence DESC, a.updated_at DESC
            LIMIT ?
            """,
            (like, like, like, like, like, like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()
        return [self._decode_row(dict(row)) for row in rows]

    def get_actor_statistics(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS count FROM actors")
        total = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT actor_type, COUNT(*) AS count
            FROM actors
            GROUP BY actor_type
            ORDER BY count DESC
            """
        )
        by_type = [dict(row) for row in cur.fetchall()]
        conn.close()

        return {"actors_total": total, "actors_by_type": by_type}

    def _decode_row(self, row: dict):
        for field in [
            "responsibilities_json",
            "owned_objects_json",
            "participates_in_json",
            "interactions_json",
            "permissions_json",
            "evidence_json",
        ]:
            try:
                row[field.replace("_json", "")] = json.loads(row.get(field) or "[]")
            except Exception:
                row[field.replace("_json", "")] = []
        return row

