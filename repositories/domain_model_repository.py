import json

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class DomainModelRepository:
    def __init__(self):
        init_fact_schema()

    def upsert_domain_object(
        self,
        entity_id: int,
        name: str,
        description: str | None = None,
        object_type: str = "business_object",
        attributes: list[dict] | None = None,
        relationships: list[dict] | None = None,
        rules: list[dict] | None = None,
        lifecycle: list[dict] | None = None,
        evidence: list[dict] | None = None,
        confidence: float = 0.7,
    ):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO domain_objects (
                entity_id,
                name,
                description,
                object_type,
                attributes_json,
                relationships_json,
                rules_json,
                lifecycle_json,
                evidence_json,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                object_type = excluded.object_type,
                attributes_json = excluded.attributes_json,
                relationships_json = excluded.relationships_json,
                rules_json = excluded.rules_json,
                lifecycle_json = excluded.lifecycle_json,
                evidence_json = excluded.evidence_json,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                entity_id,
                name,
                description,
                object_type,
                json.dumps(attributes or [], ensure_ascii=False),
                json.dumps(relationships or [], ensure_ascii=False),
                json.dumps(rules or [], ensure_ascii=False),
                json.dumps(lifecycle or [], ensure_ascii=False),
                json.dumps(evidence or [], ensure_ascii=False),
                confidence,
            ),
        )

        conn.commit()
        conn.close()

    def list_domain_objects(self, limit: int = 300):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                d.*,
                e.entity_type,
                eo.ontology_type
            FROM domain_objects d
            JOIN entities e ON e.id = d.entity_id
            LEFT JOIN entity_ontology eo ON eo.entity_id = e.id
            ORDER BY d.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cur.fetchall()
        conn.close()

        return [self._decode_row(dict(row)) for row in rows]

    def search_domain_objects(self, query: str, limit: int = 300):
        query = (query or "").strip()

        if not query:
            return self.list_domain_objects(limit=limit)

        like = f"%{query}%"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                d.*,
                e.entity_type,
                eo.ontology_type
            FROM domain_objects d
            JOIN entities e ON e.id = d.entity_id
            LEFT JOIN entity_ontology eo ON eo.entity_id = e.id
            WHERE d.name LIKE ?
               OR d.description LIKE ?
               OR d.object_type LIKE ?
               OR d.attributes_json LIKE ?
               OR d.relationships_json LIKE ?
               OR d.rules_json LIKE ?
            ORDER BY d.confidence DESC, d.updated_at DESC
            LIMIT ?
            """,
            (like, like, like, like, like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [self._decode_row(dict(row)) for row in rows]

    def get_domain_object(self, domain_object_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                d.*,
                e.entity_type,
                eo.ontology_type
            FROM domain_objects d
            JOIN entities e ON e.id = d.entity_id
            LEFT JOIN entity_ontology eo ON eo.entity_id = e.id
            WHERE d.id = ?
            """,
            (domain_object_id,),
        )

        row = cur.fetchone()
        conn.close()

        return self._decode_row(dict(row)) if row else None

    def get_domain_model_statistics(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS count FROM domain_objects")
        total = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT object_type, COUNT(*) AS count
            FROM domain_objects
            GROUP BY object_type
            ORDER BY count DESC
            """
        )
        by_type = [dict(row) for row in cur.fetchall()]

        conn.close()

        return {
            "domain_objects_total": total,
            "domain_objects_by_type": by_type,
        }

    def _decode_row(self, row: dict):
        for field in [
            "attributes_json",
            "relationships_json",
            "rules_json",
            "lifecycle_json",
            "evidence_json",
        ]:
            try:
                row[field.replace("_json", "")] = json.loads(row.get(field) or "[]")
            except Exception:
                row[field.replace("_json", "")] = []

        return row

