import json

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class RelationshipRepository:
    def __init__(self):
        init_fact_schema()

    def upsert_relationship(
        self,
        from_entity_id: int,
        to_entity_id: int,
        predicate: str,
        fact_id: int | None = None,
        confidence: float = 0.7,
        evidence: str | None = None,
        source: str | None = None,
        metadata: dict | None = None,
    ):
        predicate = (predicate or "").strip()

        if not from_entity_id or not to_entity_id or not predicate:
            return None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, confidence
            FROM entity_relationships
            WHERE from_entity_id = ?
              AND to_entity_id = ?
              AND predicate = ?
              AND COALESCE(fact_id, 0) = COALESCE(?, 0)
            LIMIT 1
            """,
            (from_entity_id, to_entity_id, predicate, fact_id),
        )

        existing = cur.fetchone()

        if existing:
            relationship_id = existing["id"]
            new_confidence = max(float(existing["confidence"] or 0), float(confidence or 0.7))

            cur.execute(
                """
                UPDATE entity_relationships
                SET confidence = ?,
                    evidence = COALESCE(?, evidence),
                    source = COALESCE(?, source),
                    metadata_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    new_confidence,
                    evidence,
                    source,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    relationship_id,
                ),
            )

            conn.commit()
            conn.close()
            return relationship_id

        cur.execute(
            """
            INSERT INTO entity_relationships (
                from_entity_id,
                to_entity_id,
                predicate,
                fact_id,
                confidence,
                evidence,
                source,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                from_entity_id,
                to_entity_id,
                predicate,
                fact_id,
                confidence,
                evidence,
                source,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )

        relationship_id = cur.lastrowid

        conn.commit()
        conn.close()

        return relationship_id

    def list_relationships(self, limit: int = 500):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                r.*,
                fe.name AS from_entity_name,
                fe.entity_type AS from_entity_type,
                te.name AS to_entity_name,
                te.entity_type AS to_entity_type,
                f.subject AS fact_subject,
                f.predicate AS fact_predicate,
                f.object AS fact_object
            FROM entity_relationships r
            JOIN entities fe ON fe.id = r.from_entity_id
            JOIN entities te ON te.id = r.to_entity_id
            LEFT JOIN facts f ON f.id = r.fact_id
            ORDER BY r.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_relationships(self, query: str, limit: int = 500):
        query = (query or "").strip()

        if not query:
            return self.list_relationships(limit=limit)

        like = f"%{query}%"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                r.*,
                fe.name AS from_entity_name,
                fe.entity_type AS from_entity_type,
                te.name AS to_entity_name,
                te.entity_type AS to_entity_type,
                f.subject AS fact_subject,
                f.predicate AS fact_predicate,
                f.object AS fact_object
            FROM entity_relationships r
            JOIN entities fe ON fe.id = r.from_entity_id
            JOIN entities te ON te.id = r.to_entity_id
            LEFT JOIN facts f ON f.id = r.fact_id
            WHERE fe.name LIKE ?
               OR te.name LIKE ?
               OR r.predicate LIKE ?
               OR r.source LIKE ?
               OR r.evidence LIKE ?
            ORDER BY r.confidence DESC, r.updated_at DESC
            LIMIT ?
            """,
            (like, like, like, like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_relationship_counts(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT predicate, COUNT(*) AS count
            FROM entity_relationships
            GROUP BY predicate
            ORDER BY count DESC
            LIMIT 100
            """
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_entity_neighborhood(self, entity_name: str, limit: int = 200):
        entity_name = (entity_name or "").strip()

        if not entity_name:
            return []

        like = f"%{entity_name}%"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                r.*,
                fe.name AS from_entity_name,
                fe.entity_type AS from_entity_type,
                te.name AS to_entity_name,
                te.entity_type AS to_entity_type,
                f.subject AS fact_subject,
                f.predicate AS fact_predicate,
                f.object AS fact_object
            FROM entity_relationships r
            JOIN entities fe ON fe.id = r.from_entity_id
            JOIN entities te ON te.id = r.to_entity_id
            LEFT JOIN facts f ON f.id = r.fact_id
            WHERE fe.name LIKE ?
               OR te.name LIKE ?
            ORDER BY r.confidence DESC, r.updated_at DESC
            LIMIT ?
            """,
            (like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

