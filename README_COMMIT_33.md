# Commit 33 — Project Chat 2.0: Intent-Aware Retrieval

## Goal

Improve Project Chat quality by making retrieval intent-aware and model-first.

Before:

```text
Question → keyword search → LLM
```

After:

```text
Question
  ↓
Intent classifier
  ↓
Project Summary / Entity Profiles / Relationships / Facts / Memory / Chunks
  ↓
LLM answer with evidence
```

## Added / replaced

```text
ai/question_intent.py
repositories/chat_context_repository.py
ai/project_chat.py
ui/floating_project_chat.py
```

## New intents

```text
project_overview
entity_deep_dive
relationships
requirements
risks
open_questions
integrations
processes
decisions
general
```

## Retrieval improvements

For overview questions:
- uses Project Summary first;
- adds high-value facts;
- avoids random chunks dominating the answer.

For entity questions:
- resolves entity profiles;
- adds facts grouped by entity;
- adds relationships around entity.

For graph/process questions:
- retrieves relationships first;
- includes neighborhood around matching entities.

For risks/requirements/open questions:
- filters facts and knowledge by relevant types.

## Chat prompt improvement

Chat now receives:

```text
QUESTION INTENT
PROJECT SUMMARY
ENTITY PROFILES
ENTITY RELATIONSHIPS
CANONICAL FACTS
PROJECT MEMORY ITEMS
SOURCE CHUNKS
```

and uses them in that priority order.

## Apply

Copy:

```text
ai/question_intent.py
repositories/chat_context_repository.py
ai/project_chat.py
ui/floating_project_chat.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 33 - Add intent-aware project chat"
```
