import json
from typing import Iterable

from core.fact_types import CanonicalFact
from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class FactRepository:
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        init_fact_schema()

    def save_fact(self, fact: dict | CanonicalFact) -> int | None:
        if isinstance(fact, CanonicalFact):
            data = fact.normalized()
        else:
            data = self._normalize_fact_dict(fact)

        if not data["subject"] or not data["predicate"] or not data["object"]:
            return None

        existing_id = self._find_similar_fact(data)

        if existing_id:
            self._update_existing_fact(existing_id, data)
            return existing_id

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO facts (
                subject,
                predicate,
                object,
                fact_type,
                confidence,
                status,
                evidence,
                source,
                metadata_json,
                project_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["subject"],
                data["predicate"],
                data["object"],
                data["fact_type"],
                data["confidence"],
                data["status"],
                data.get("evidence"),
                data.get("source"),
                json.dumps(data.get("metadata") or {}, ensure_ascii=False),
                self.project_id,
            ),
        )

        fact_id = cur.lastrowid

        if data.get("evidence"):
            cur.execute(
                """
                INSERT INTO fact_evidence (fact_id, evidence_type, evidence_ref, quote)
                VALUES (?, ?, ?, ?)
                """,
                (
                    fact_id,
                    "source",
                    data.get("source"),
                    data.get("evidence"),
                ),
            )

        conn.commit()
        conn.close()

        return fact_id

    def save_facts(self, facts: Iterable[dict | CanonicalFact]):
        saved = 0
        skipped = 0
        ids = []
        errors = []

        for fact in facts:
            try:
                fact_id = self.save_fact(fact)
                if fact_id:
                    saved += 1
                    ids.append(fact_id)
                else:
                    skipped += 1
            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        return {
            "saved": saved,
            "skipped": skipped,
            "ids": ids,
            "errors": errors,
        }

    def list_facts(self, limit: int = 200, fact_type: str | None = None):
        conn = get_connection()
        cur = conn.cursor()

        if fact_type:
            cur.execute(
                """
                SELECT *
                FROM facts
                WHERE fact_type = ? AND project_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (fact_type, self.project_id, limit),
            )
        else:
            cur.execute(
                """
                SELECT *
                FROM facts
                WHERE project_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (self.project_id, limit),
            )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_facts(self, query: str, limit: int = 100):
        query = (query or "").strip()

        if not query:
            return self.list_facts(limit=limit)

        terms = [term for term in query.split() if len(term) >= 3][:8]
        like_terms = [f"%{term}%" for term in terms] or [f"%{query}%"]

        where = " OR ".join(
            ["subject LIKE ? OR predicate LIKE ? OR object LIKE ? OR source LIKE ?" for _ in like_terms]
        )

        params = []
        for term in like_terms:
            params.extend([term, term, term, term])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT *
            FROM facts
            WHERE project_id = ? AND ({where})
            ORDER BY confidence DESC, updated_at DESC
            LIMIT ?
            """,
            [self.project_id] + params + [limit],
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_fact_counts(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT fact_type, COUNT(*) AS count
            FROM facts
            WHERE project_id = ?
            GROUP BY fact_type
            ORDER BY count DESC
            """,
            (self.project_id,),
        )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def _find_similar_fact(self, data: dict) -> int | None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id
            FROM facts
            WHERE LOWER(subject) = LOWER(?)
              AND LOWER(predicate) = LOWER(?)
              AND LOWER(object) = LOWER(?)
              AND project_id = ?
            LIMIT 1
            """,
            (data["subject"], data["predicate"], data["object"], self.project_id),
        )

        row = cur.fetchone()
        conn.close()

        return row["id"] if row else None

    def _update_existing_fact(self, fact_id: int, data: dict):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT confidence, version
            FROM facts
            WHERE id = ?
            """,
            (fact_id,),
        )

        row = cur.fetchone()

        if not row:
            conn.close()
            return

        new_confidence = max(float(row["confidence"] or 0), float(data["confidence"] or 0.7))

        cur.execute(
            """
            UPDATE facts
            SET confidence = ?,
                status = ?,
                evidence = COALESCE(?, evidence),
                source = COALESCE(?, source),
                version = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                new_confidence,
                data["status"],
                data.get("evidence"),
                data.get("source"),
                int(row["version"] or 1) + 1,
                fact_id,
            ),
        )

        if data.get("evidence"):
            cur.execute(
                """
                INSERT INTO fact_evidence (fact_id, evidence_type, evidence_ref, quote)
                VALUES (?, ?, ?, ?)
                """,
                (
                    fact_id,
                    "source",
                    data.get("source"),
                    data.get("evidence"),
                ),
            )

        conn.commit()
        conn.close()

    def _normalize_fact_dict(self, fact: dict):
        confidence = fact.get("confidence", 0.7)

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.7

        confidence = max(0.0, min(confidence, 1.0))

        return {
            "subject": str(fact.get("subject") or "").strip()[:240],
            "predicate": str(fact.get("predicate") or "").strip()[:160],
            "object": str(fact.get("object") or "").strip()[:1200],
            "fact_type": str(fact.get("fact_type") or fact.get("type") or "unknown").strip()[:80],
            "confidence": confidence,
            "status": str(fact.get("status") or "proposed").strip()[:80],
            "evidence": fact.get("evidence"),
            "source": fact.get("source"),
            "metadata": fact.get("metadata") or {},
        }

