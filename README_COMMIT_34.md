# Commit 34 — Ontology Builder

## Goal

Classify Entities into stable Project Model ontology types.

Before:

```text
Merchant → entity_type: unknown
Worksheet → entity_type: related_object
Funding → entity_type: process
```

After:

```text
Merchant → ontology_type: actor
Advance → ontology_type: business_object
Funding → ontology_type: process
Plaid → ontology_type: integration
Worksheet → ontology_type: module
```

## Added / replaced

```text
core/ontology.py
memory/fact_schema.py
repositories/ontology_repository.py
builders/ontology_builder.py
ui/ontology.py
ui/workspace/model.py
```

## New DB table

```text
entity_ontology
```

Columns:

```text
entity_id
ontology_type
confidence
classification_method
reason
metadata_json
created_at
updated_at
```

## New UI

Project Model now has:

```text
🧬 Ontology
```

It can:
- classify/refresh entity ontology;
- show ontology counts;
- search classified entities;
- inspect classification confidence and reason.

## Classification method

Commit 34 uses deterministic heuristics first.

This is intentional:
- fast;
- cheap/free;
- predictable;
- safe baseline before AI classification.

Later commits can add AI-assisted classification for:
- unknown entities;
- low-confidence entities;
- ambiguous entities.

## Apply

Copy:

```text
core/ontology.py
memory/fact_schema.py
repositories/ontology_repository.py
builders/ontology_builder.py
ui/ontology.py
ui/workspace/model.py
```

Run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → Ontology → Classify / Refresh Entity Ontology
```

Then rebuild:

```text
Project Model → Project Summary → Build / Refresh Project Summary
```

Commit:

```powershell
git add .
git commit -m "Commit 34 - Add ontology builder"
```
