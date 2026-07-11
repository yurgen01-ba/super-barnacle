import json

from core.ontology import normalize_ontology_type
from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class OntologyRepository:
    def __init__(self):
        init_fact_schema()

    def ensure_schema(self):
        init_fact_schema()

    def upsert_entity_ontology(
        self,
        entity_id: int,
        ontology_type: str,
        confidence: float = 0.3,
        classification_method: str = "heuristic",
        reason: str | None = None,
        metadata: dict | None = None,
    ):
        ontology_type = normalize_ontology_type(ontology_type)

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.3

        confidence = max(0.0, min(confidence, 1.0))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO entity_ontology (
                entity_id, ontology_type, confidence, classification_method, reason, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_id) DO UPDATE SET
                ontology_type = excluded.ontology_type,
                confidence = excluded.confidence,
                classification_method = excluded.classification_method,
                reason = excluded.reason,
                metadata_json = excluded.metadata_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                entity_id,
                ontology_type,
                confidence,
                classification_method,
                reason,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )

        conn.commit()
        conn.close()

    def list_entity_ontology(self, limit: int = 500):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                eo.*,
                e.name AS entity_name,
                e.entity_type AS entity_type,
                e.description AS entity_description
            FROM entity_ontology eo
            JOIN entities e ON e.id = eo.entity_id
            ORDER BY eo.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def search_entity_ontology(self, query: str, limit: int = 500):
        query = (query or "").strip()

        if not query:
            return self.list_entity_ontology(limit=limit)

        like = f"%{query}%"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                eo.*,
                e.name AS entity_name,
                e.entity_type AS entity_type,
                e.description AS entity_description
            FROM entity_ontology eo
            JOIN entities e ON e.id = eo.entity_id
            WHERE e.name LIKE ?
               OR e.entity_type LIKE ?
               OR eo.ontology_type LIKE ?
               OR eo.reason LIKE ?
            ORDER BY eo.confidence DESC, eo.updated_at DESC
            LIMIT ?
            """,
            (like, like, like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_ontology_counts(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT ontology_type, COUNT(*) AS count
            FROM entity_ontology
            GROUP BY ontology_type
            ORDER BY count DESC
            """
        )

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

