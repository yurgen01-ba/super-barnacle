from memory.db import get_connection


class Timeline:
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id

    def add_event(self, event_type: str, title: str, source: str = "unknown"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO timeline (event_type, title, source, project_id)
            VALUES (?, ?, ?, ?)
            """,
            (event_type, title, source, self.project_id),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM timeline WHERE project_id = ? ORDER BY created_at DESC", (self.project_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM timeline WHERE project_id = ?", (self.project_id,))
        conn.commit()
        conn.close()

