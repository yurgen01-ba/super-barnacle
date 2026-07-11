# Commit 100 — Fix Project Graph Hydrate Method

## Problem

Chat send button fails with:

```text
AttributeError: 'ProjectGraphStore' object has no attribute 'hydrate'
```

`GraphRetrieverV2` expects `project_graph_store.hydrate(project_id)`, but the currently applied `ProjectGraphStore` does not contain this method.

## Fix

Replaces:

```text
repositories/project_graph_store.py
graph/project_graph_hydration.py
```

## What changed

- Adds `ProjectGraphStore.hydrate()`.
- Keeps runtime graph usable even if persistence has issues.
- Keeps `ProjectGraphHydrationService` backward-compatible.
- Fixes chat send button crash.

## Commit

```powershell
git add repositories/project_graph_store.py graph/project_graph_hydration.py README_COMMIT_100_FIX_PROJECT_GRAPH_HYDRATE_METHOD.md
git commit -m "Commit 100 - Fix Project Graph hydrate method"
```
