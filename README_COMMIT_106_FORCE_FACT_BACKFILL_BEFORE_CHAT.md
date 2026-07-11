# Commit 106 — Force Fact Backfill before Chat

## Goal

Before chat reads Project Graph, hydrate it and backfill from FactRepository if graph is empty.

## Changed

```text
graph/project_graph_hydration.py
graph/graph_retriever_v2.py
```

## Commit

```powershell
git add graph/project_graph_hydration.py graph/graph_retriever_v2.py README_COMMIT_106_FORCE_FACT_BACKFILL_BEFORE_CHAT.md
git commit -m "Commit 106 - Force FactRepository backfill before chat"
```
