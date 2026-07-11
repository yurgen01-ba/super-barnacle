import json
from collections import defaultdict

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class EntityRepository:
    def __init__(self):
        init_fact_schema()

    def upsert_entity(
        self,
        name: str,
        entity_type: str = "unknown",
        description: str | None = None,
        metadata: dict | None = None,
        confidence: float = 0.7,
    ):
        name = (name or "").strip()

        if not name:
            return None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO entities (name, entity_type, description, metadata_json, confidence)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                entity_type = excluded.entity_type,
                description = COALESCE(excluded.description, entities.description),
                metadata_json = excluded.metadata_json,
                confidence = MAX(entities.confidence, excluded.confidence),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                name,
                entity_type,
                description,
                json.dumps(metadata or {}, ensure_ascii=False),
                confidence,
            ),
        )

        conn.commit()

        cur.execute("SELECT id FROM entities WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()

        return row["id"] if row else None

    def link_fact(
        self,
        entity_id: int,
        fact_id: int,
        relation_type: str = "about",
    ):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id
            FROM entity_facts
            WHERE entity_id = ?
              AND fact_id = ?
              AND relation_type = ?
            LIMIT 1
            """,
            (entity_id, fact_id, relation_type),
        )

        existing = cur.fetchone()

        if existing:
            conn.close()
            return existing["id"]

        cur.execute(
            """
            INSERT INTO entity_facts (entity_id, fact_id, relation_type)
            VALUES (?, ?, ?)
            """,
            (entity_id, fact_id, relation_type),
        )

        link_id = cur.lastrowid

        conn.commit()
        conn.close()

        return link_id

    def list_entities(self, limit: int = 200):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                e.*,
                COUNT(ef.id) AS facts_count
            FROM entities e
            LEFT JOIN entity_facts ef ON ef.entity_id = e.id
            GROUP BY e.id
            ORDER BY e.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_entity(self, entity_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM entities
            WHERE id = ?
            """,
            (entity_id,),
        )

        row = cur.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_entity_by_name(self, name: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM entities
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,),
        )

        row = cur.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_entity_facts(self, entity_id: int, limit: int = 300):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                f.*,
                ef.relation_type
            FROM entity_facts ef
            JOIN facts f ON f.id = ef.fact_id
            WHERE ef.entity_id = ?
            ORDER BY f.confidence DESC, f.updated_at DESC
            LIMIT ?
            """,
            (entity_id, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def build_entity_profile(self, entity_id: int):
        entity = self.get_entity(entity_id)

        if not entity:
            return None

        facts = self.get_entity_facts(entity_id)

        grouped = defaultdict(list)

        for fact in facts:
            grouped[fact.get("fact_type") or "unknown"].append(fact)

        outgoing_relationships = [
            fact for fact in facts
            if fact.get("relation_type") in ("subject", "about")
            and fact.get("predicate")
            and fact.get("object")
        ]

        incoming_relationships = [
            fact for fact in facts
            if fact.get("relation_type") == "object"
        ]

        return {
            "entity": entity,
            "facts": facts,
            "grouped_facts": dict(grouped),
            "outgoing_relationships": outgoing_relationships,
            "incoming_relationships": incoming_relationships,
            "facts_count": len(facts),
        }

    def search_entities(self, query: str, limit: int = 100):
        query = (query or "").strip()

        if not query:
            return self.list_entities(limit=limit)

        like = f"%{query}%"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                e.*,
                COUNT(ef.id) AS facts_count
            FROM entities e
            LEFT JOIN entity_facts ef ON ef.entity_id = e.id
            WHERE e.name LIKE ?
               OR e.entity_type LIKE ?
               OR e.description LIKE ?
            GROUP BY e.id
            ORDER BY facts_count DESC, e.updated_at DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

