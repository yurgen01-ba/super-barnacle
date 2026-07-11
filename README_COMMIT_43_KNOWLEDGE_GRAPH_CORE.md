# Commit 43 — Knowledge Graph Core

## Goal

Add the first implementation of Project Knowledge Graph without breaking existing repositories or UI.

This commit introduces a graph adapter layer.

Existing repositories remain the source of data for now.

## Added

```text
models/knowledge_node.py
models/knowledge_edge.py
models/evidence.py

graph/__init__.py
graph/graph_types.py
graph/graph_builder.py
graph/graph_repository.py
graph/graph_query.py
graph/graph_serializer.py
graph/graph_validator.py
```

## Architecture

```text
Existing repositories
    ↓
GraphBuilder
    ↓
KnowledgeGraph
    ↓
GraphRepository
    ↓
GraphRetriever
    ↓
AI / UI / future Project Model
```

## Important rule

New AI functionality should use:

```python
GraphRepository
GraphRetriever
```

instead of directly depending on:

```python
FactRepository
EntityRepository
ActorRepository
ProcessRepository
```

## What works now

- Lightweight `KnowledgeNode`
- Lightweight `KnowledgeEdge`
- Lightweight `Evidence`
- In-memory `KnowledgeGraph`
- Adapter-based `GraphBuilder`
- `GraphRepository`
- `GraphRetriever`
- Markdown/dict serialization
- Basic graph validation
- Weak keyword-based initial relationships

## What this commit does NOT do

- Does not change DB schema.
- Does not migrate existing data.
- Does not remove old repositories.
- Does not replace AI chat yet.
- Does not add UI graph inspector yet.

## Next commits

### Commit 44

Graph Query Engine:
- better traversal;
- node profiles;
- relationship paths;
- impact context.

### Commit 45

AI Chat over Graph:
- route overview questions to GraphRetriever;
- force answer language;
- improve context quality;
- add graph statistics to answers.

### Commit 46

Knowledge Graph Inspector:
- advanced UI for graph browsing.

## Commit

```powershell
git add graph models/knowledge_node.py models/knowledge_edge.py models/evidence.py README_COMMIT_43_KNOWLEDGE_GRAPH_CORE.md
git commit -m "Commit 43 - Add Knowledge Graph core"
```
