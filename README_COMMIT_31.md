# Commit 31 — Relationship Builder

## Goal

Make Project Brain start reasoning over project structure, not only storing facts/entities.

This commit adds the first graph layer:

```text
Entity A → predicate → Entity B
```

## Added / replaced

```text
memory/fact_schema.py
repositories/relationship_repository.py
builders/relationship_builder.py
ui/relationships.py
repositories/chat_context_repository.py
ai/project_chat.py
ui/workspace/model.py
```

## New table

```text
entity_relationships
```

Columns:

```text
id
from_entity_id
to_entity_id
predicate
fact_id
confidence
evidence
source
metadata_json
created_at
updated_at
```

## Pipeline

```text
Canonical Facts
  ↓
Entities
  ↓
Relationship Builder
  ↓
Entity Relationships
  ↓
Graph-aware Project Chat
```

## New UI

Project Model now has:

```text
🔗 Relationships
```

It can:
- build/refresh relationships from facts;
- search relationships;
- show relationship counts by predicate;
- inspect entity neighborhood.

## Chat improvement

Project Chat context now includes:

```text
ENTITY RELATIONSHIPS
```

So questions like:

- "What is connected to Merchant?"
- "Who approves Advance?"
- "What does Funding depend on?"

can use graph relationships, not only keyword search.

## Apply

Copy:

```text
memory/fact_schema.py
repositories/relationship_repository.py
builders/relationship_builder.py
ui/relationships.py
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
Project Model → Relationships → Build / Refresh Relationships from Facts
```

Commit:

```powershell
git add .
git commit -m "Commit 31 - Add relationship builder"
```
