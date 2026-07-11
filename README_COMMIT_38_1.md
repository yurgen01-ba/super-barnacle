# Commit 38.1 — AI Analyst Retrieval Fix

## Goal

Fix the current Project Chat / AI Analyst behavior where broad overview questions such as:

```text
о чем проект вкратце
```

could be answered from a random transcript chunk instead of the structured Project Model.

## Added / replaced

```text
ai/question_intent.py
repositories/chat_context_repository.py
ai/project_chat.py
```

## What changed

### 1. Better intent detection

Overview questions are now detected more reliably:

```text
о чем проект
о чём проект
вкратце
коротко
что это за система
```

These are classified as:

```text
project_overview
```

### 2. Model-first retrieval

The chat context now prioritizes:

```text
Project Summary
Domain Objects
Actors
Processes
Entity Profiles
Relationships
Canonical Facts
Memory Items
Chunks only as fallback
```

For overview questions, chunks are not used unless the structured model is almost empty.

### 3. Optional repository imports

`ActorsRepository`, `DomainModelRepository`, and `ProcessRepository` are imported safely.
If one of these layers is absent in the local branch, chat still works.

### 4. Stronger answer prompt

The prompt now explicitly tells the model:

```text
Do not summarize a random transcript segment.
Use Project Summary + Domain Objects + Actors + Processes + Facts.
```

## Apply

Copy these files into the project:

```text
ai/question_intent.py
repositories/chat_context_repository.py
ai/project_chat.py
```

Run:

```powershell
python -m streamlit run app.py
```

Test with:

```text
о чем проект вкратце
```

Commit:

```powershell
git add ai/question_intent.py repositories/chat_context_repository.py ai/project_chat.py README_COMMIT_38_1.md
git commit -m "Commit 38.1 - Fix AI Analyst retrieval"
```
