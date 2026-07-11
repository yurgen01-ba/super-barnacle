from memory.db import get_connection


class Timeline:
    def add_event(self, event_type: str, title: str, source: str = "unknown"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO timeline (event_type, title, source)
            VALUES (?, ?, ?)
            """,
            (event_type, title, source),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM timeline ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM timeline")
        conn.commit()
        conn.close()

