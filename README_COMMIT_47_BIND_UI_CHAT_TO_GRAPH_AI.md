# Commit 47 — Bind UI Chat to Graph AI

## Goal

Make UI v2 chat use graph-first AI answering.

## Changed

```text
ui_v2/layout/chat.py
```

## What changed

- Replaced old AI chat dependency with `answer_project_question_over_graph`.
- Chat now reads Project Knowledge Graph.
- UI copy explicitly says old RAG context is not used.

## Commit

```powershell
git add ui_v2/layout/chat.py README_COMMIT_47_BIND_UI_CHAT_TO_GRAPH_AI.md
git commit -m "Commit 47 - Bind UI chat to graph AI"
```
