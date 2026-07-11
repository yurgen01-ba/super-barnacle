from memory.db import get_connection
from memory.schema import KnowledgeItem


class ProjectMemory:
    def add(self, item: KnowledgeItem):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO knowledge (type, title, content, source)
            VALUES (?, ?, ?, ?)
            """,
            (item.type, item.title, item.content, item.source),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM knowledge ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM knowledge")
        conn.commit()
        conn.close()

