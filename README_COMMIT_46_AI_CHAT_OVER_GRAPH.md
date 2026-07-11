# Commit 46 — AI Chat over Graph

## Goal

Add graph-first AI answering function.

## Added

```text
ai/graph_answering.py
```

## What it does

- Uses GraphContextRepository.
- Builds graph-first prompt.
- Forces answer language to match user question.
- Explicitly prevents Chinese unless user asked in Chinese.
- Avoids old RAG context.
- Falls back to deterministic graph context if no model provider is available.

## Commit

```powershell
git add ai/graph_answering.py README_COMMIT_46_AI_CHAT_OVER_GRAPH.md
git commit -m "Commit 46 - Add AI answering over graph"
```
