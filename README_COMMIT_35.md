# Commit 35 — Domain Model Builder

## Goal

Build the first DDD-like Domain Model layer from Ontology, Entities, Facts, and Relationships.

This is the next step after Ontology Builder.

## New concept

A Domain Object is a structured model object with:

```text
name
description
object_type
attributes
relationships
rules
lifecycle
evidence
confidence
```

Examples:

```text
Merchant
Advance
Worksheet
Funding
Payment
Draw
Fee
LoCi
Report
Dashboard
```

## Added / replaced

```text
memory/fact_schema.py
repositories/domain_model_repository.py
builders/domain_model_builder.py
ui/domain_model.py
ui/workspace/model.py
repositories/project_repository.py
```

## New DB table

```text
domain_objects
```

Columns:

```text
entity_id
name
description
object_type
attributes_json
relationships_json
rules_json
lifecycle_json
evidence_json
confidence
created_at
updated_at
```

## New UI

Project Model now has:

```text
🏛️ Domain Model
```

It can:
- build/refresh Domain Model;
- search domain objects;
- inspect attributes/states;
- inspect lifecycle hints;
- inspect relationships;
- inspect rules/requirements/risks;
- inspect evidence.

## Build order

Use this order:

```text
1. Canonical Facts
2. Entities
3. Relationships
4. Ontology
5. Domain Model
6. Project Summary
```

## Apply

Copy:

```text
memory/fact_schema.py
repositories/domain_model_repository.py
builders/domain_model_builder.py
ui/domain_model.py
ui/workspace/model.py
repositories/project_repository.py
```

Run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → Domain Model → Build / Refresh Domain Model
```

Commit:

```powershell
git add .
git commit -m "Commit 35 - Add domain model builder"
```
