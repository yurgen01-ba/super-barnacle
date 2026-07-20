from memory.db import get_connection
from memory.schema import KnowledgeItem


class ProjectMemory:
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id

    def add(self, item: KnowledgeItem):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO knowledge (type, title, content, source, project_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item.type, item.title, item.content, item.source, self.project_id),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM knowledge WHERE project_id = ? ORDER BY created_at DESC", (self.project_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM knowledge WHERE project_id = ?", (self.project_id,))
        conn.commit()
        conn.close()

