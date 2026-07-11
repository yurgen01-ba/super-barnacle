# Commit 44 — Graph Query Engine

## Goal

Move retrieval away from plain RAG toward graph-first context building.

## Added

```text
graph/graph_query_engine.py
```

## What it does

- Finds relevant Knowledge Nodes.
- Expands one-hop related nodes.
- Builds structured AI context.
- Provides `GraphContext.to_prompt_context()`.

## Commit

```powershell
git add graph/graph_query_engine.py README_COMMIT_44_GRAPH_QUERY_ENGINE.md
git commit -m "Commit 44 - Add Graph Query Engine"
```
