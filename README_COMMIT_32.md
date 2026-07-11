# Commit 32 — Project Summary Builder

## Goal

Add a stable Project Summary layer so Project Chat no longer has to infer the whole project from random memory items.

## Added / replaced

```text
repositories/project_repository.py
builders/project_summary_builder.py
ui/project_summary.py
repositories/chat_context_repository.py
ai/project_chat.py
ui/workspace/model.py
```

## New flow

```text
Canonical Facts
  ↓
Entities
  ↓
Relationships
  ↓
Project Summary Builder
  ↓
Project Summary
  ↓
Project Chat
```

## UI

Project Model now has a new first tab:

```text
📌 Project Summary
```

It can:
- show model statistics;
- build/refresh Project Summary;
- display latest summary;
- show previous summary versions.

## Chat improvement

Project Chat now includes `PROJECT SUMMARY` in context and is instructed to use it first for overview questions:

- "Что это за проект?"
- "Опиши суть проекта"
- "Какие основные процессы?"
- "Какие основные сущности?"
- "Какие интеграции?"

## Apply

Copy:

```text
repositories/project_repository.py
builders/project_summary_builder.py
ui/project_summary.py
repositories/chat_context_repository.py
ai/project_chat.py
ui/workspace/model.py
```

Run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → Project Summary → Build / Refresh Project Summary
```

Commit:

```powershell
git add .
git commit -m "Commit 32 - Add project summary builder"
```
