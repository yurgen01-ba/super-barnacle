from memory.db import get_connection
from utils.text import chunk_text


class SourceRepository:
    """
    Stores processed source documents and their chunks.

    This is intentionally separate from ProjectMemory:
    - documents/chunks = source material that entered the system
    - knowledge = extracted facts/requirements/risks/decisions
    """

    def save_document(
        self,
        name: str,
        source_type: str,
        text: str,
        source_ref: str | None = None,
        max_chunk_chars: int = 10000,
        project_id: str = "default",
    ):
        text = text or ""
        chunks = chunk_text(text, max_chars=max_chunk_chars) if text.strip() else []

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO documents (name, source_type, source_ref, text_length, project_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, source_type, source_ref, len(text), project_id),
        )

        document_id = cur.lastrowid

        for index, chunk in enumerate(chunks, start=1):
            cur.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, content, content_length)
                VALUES (?, ?, ?, ?)
                """,
                (document_id, index, chunk, len(chunk)),
            )

        conn.commit()
        conn.close()

        return {
            "document_id": document_id,
            "chunks_count": len(chunks),
            "text_length": len(text),
        }

    def list_documents(self, project_id: str = "default"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                d.*,
                COUNT(c.id) AS chunks_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            WHERE d.project_id = ?
            GROUP BY d.id
            ORDER BY d.created_at DESC
        """, (project_id,))

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def list_chunks(self, document_id: int | None = None, limit: int = 100):
        conn = get_connection()
        cur = conn.cursor()

        if document_id is None:
            cur.execute(
                """
                SELECT
                    c.*,
                    d.name AS document_name,
                    d.source_type AS source_type
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                ORDER BY c.created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cur.execute(
                """
                SELECT
                    c.*,
                    d.name AS document_name,
                    d.source_type AS source_type
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.document_id = ?
                ORDER BY c.chunk_index ASC
                LIMIT ?
                """,
                (document_id, limit),
            )

        rows = cur.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def clear(self, project_id: str = "default"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chunks WHERE document_id IN (SELECT id FROM documents WHERE project_id = ?)", (project_id,))
        cur.execute("DELETE FROM documents WHERE project_id = ?", (project_id,))
        conn.commit()
        conn.close()

