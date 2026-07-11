from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


class PersistentProjectGraphRepository:
    """
    SQLite persistence for Project Graph nodes and edges.
    """

    def __init__(self, db_path: str | Path = "data/project_graph.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    confidence REAL,
                    status TEXT,
                    source TEXT,
                    source_id TEXT,
                    metadata_json TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_edges (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    from_node_id TEXT NOT NULL,
                    to_node_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    confidence REAL,
                    source TEXT,
                    metadata_json TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_type "
                "ON graph_nodes(project_id, node_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_graph_edges_project "
                "ON graph_edges(project_id)"
            )

    def save_node(self, node: KnowledgeNode, project_id: str = "default") -> KnowledgeNode:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO graph_nodes (
                    id, project_id, node_type, title, description, confidence,
                    status, source, source_id, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.id,
                    project_id,
                    node.node_type,
                    node.title,
                    node.description,
                    float(node.confidence or 0),
                    node.status,
                    node.source,
                    node.source_id,
                    json.dumps(node.metadata or {}, ensure_ascii=False),
                ),
            )
        return node

    def save_edge(self, edge: KnowledgeEdge, project_id: str = "default") -> KnowledgeEdge:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO graph_edges (
                    id, project_id, from_node_id, to_node_id, relationship_type,
                    confidence, source, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.id,
                    project_id,
                    edge.from_node_id,
                    edge.to_node_id,
                    edge.relationship_type,
                    float(edge.confidence or 0),
                    edge.source,
                    json.dumps(edge.metadata or {}, ensure_ascii=False),
                ),
            )
        return edge

    def load_nodes(self, project_id: str = "default") -> list[KnowledgeNode]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, node_type, title, description, confidence, status,
                       source, source_id, metadata_json
                FROM graph_nodes
                WHERE project_id = ?
                """,
                (project_id,),
            ).fetchall()

        return [
            KnowledgeNode(
                id=row[0],
                node_type=row[1],
                title=row[2],
                description=row[3] or "",
                confidence=float(row[4] or 0),
                status=row[5] or "active",
                source=row[6] or "",
                source_id=row[7],
                metadata=json.loads(row[8] or "{}"),
            )
            for row in rows
        ]

    def load_edges(self, project_id: str = "default") -> list[KnowledgeEdge]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, from_node_id, to_node_id, relationship_type,
                       confidence, source, metadata_json
                FROM graph_edges
                WHERE project_id = ?
                """,
                (project_id,),
            ).fetchall()

        return [
            KnowledgeEdge(
                id=row[0],
                from_node_id=row[1],
                to_node_id=row[2],
                relationship_type=row[3],
                confidence=float(row[4] or 0),
                source=row[5] or "",
                metadata=json.loads(row[6] or "{}"),
            )
            for row in rows
        ]

    def stats(self, project_id: str = "default") -> dict[str, int]:
        with self._connect() as conn:
            node_count = conn.execute(
                "SELECT COUNT(*) FROM graph_nodes WHERE project_id = ?",
                (project_id,),
            ).fetchone()[0]

            edge_count = conn.execute(
                "SELECT COUNT(*) FROM graph_edges WHERE project_id = ?",
                (project_id,),
            ).fetchone()[0]

            by_type = conn.execute(
                """
                SELECT node_type, COUNT(*)
                FROM graph_nodes
                WHERE project_id = ?
                GROUP BY node_type
                """,
                (project_id,),
            ).fetchall()

        return {
            "nodes": node_count,
            "edges": edge_count,
            **{row[0]: row[1] for row in by_type},
        }


persistent_project_graph_repository = PersistentProjectGraphRepository()
