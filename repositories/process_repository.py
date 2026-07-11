import json

from memory.db import get_connection
from memory.fact_schema import init_fact_schema


class ProcessRepository:
    def __init__(self):
        init_fact_schema()

    def upsert_process(
        self,
        name: str,
        description: str | None = None,
        process_type: str = "business_process",
        goal: str | None = None,
        participants: list[dict] | None = None,
        business_objects: list[dict] | None = None,
        steps: list[dict] | None = None,
        inputs: list[dict] | None = None,
        outputs: list[dict] | None = None,
        rules: list[dict] | None = None,
        exceptions: list[dict] | None = None,
        evidence: list[dict] | None = None,
        confidence: float = 0.7,
    ):
        name = (name or "").strip()
        if not name:
            return None

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO processes (
                name,
                description,
                process_type,
                goal,
                participants_json,
                business_objects_json,
                steps_json,
                inputs_json,
                outputs_json,
                rules_json,
                exceptions_json,
                evidence_json,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                process_type = excluded.process_type,
                goal = excluded.goal,
                participants_json = excluded.participants_json,
                business_objects_json = excluded.business_objects_json,
                steps_json = excluded.steps_json,
                inputs_json = excluded.inputs_json,
                outputs_json = excluded.outputs_json,
                rules_json = excluded.rules_json,
                exceptions_json = excluded.exceptions_json,
                evidence_json = excluded.evidence_json,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                name,
                description,
                process_type,
                goal,
                json.dumps(participants or [], ensure_ascii=False),
                json.dumps(business_objects or [], ensure_ascii=False),
                json.dumps(steps or [], ensure_ascii=False),
                json.dumps(inputs or [], ensure_ascii=False),
                json.dumps(outputs or [], ensure_ascii=False),
                json.dumps(rules or [], ensure_ascii=False),
                json.dumps(exceptions or [], ensure_ascii=False),
                json.dumps(evidence or [], ensure_ascii=False),
                confidence,
            ),
        )

        cur.execute("SELECT id FROM processes WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return row["id"] if row else None

    def list_processes(self, limit: int = 300):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM processes
            ORDER BY updated_at DESC, confidence DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()
        return [self._decode_row(dict(row)) for row in rows]

    def search_processes(self, query: str, limit: int = 300):
        query = (query or "").strip()
        if not query:
            return self.list_processes(limit=limit)

        like = f"%{query}%"
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM processes
            WHERE name LIKE ?
               OR description LIKE ?
               OR process_type LIKE ?
               OR goal LIKE ?
               OR participants_json LIKE ?
               OR business_objects_json LIKE ?
               OR steps_json LIKE ?
               OR rules_json LIKE ?
            ORDER BY confidence DESC, updated_at DESC
            LIMIT ?
            """,
            (like, like, like, like, like, like, like, like, limit),
        )
        rows = cur.fetchall()
        conn.close()
        return [self._decode_row(dict(row)) for row in rows]

    def get_process_statistics(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS count FROM processes")
        total = cur.fetchone()["count"]
        cur.execute(
            """
            SELECT process_type, COUNT(*) AS count
            FROM processes
            GROUP BY process_type
            ORDER BY count DESC
            """
        )
        by_type = [dict(row) for row in cur.fetchall()]
        conn.close()
        return {"processes_total": total, "processes_by_type": by_type}

    def _decode_row(self, row: dict):
        for field in [
            "participants_json",
            "business_objects_json",
            "steps_json",
            "inputs_json",
            "outputs_json",
            "rules_json",
            "exceptions_json",
            "evidence_json",
        ]:
            try:
                row[field.replace("_json", "")] = json.loads(row.get(field) or "[]")
            except Exception:
                row[field.replace("_json", "")] = []
        return row

