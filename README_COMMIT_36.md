# Commit 36 — Project Intelligence: Actors Layer

## Goal

Add the first specialized Project Intelligence layer: Actor Profiles.

Actors are not just entities. They are roles/participants with:
- responsibilities;
- owned or related business objects;
- process participation;
- interactions;
- permissions;
- evidence.

## Added / replaced

```text
models/actor.py
memory/fact_schema.py
repositories/actors_repository.py
builders/actors_builder.py
ui/actors.py
ui/workspace/model.py
repositories/project_repository.py
```

## New DB table

```text
actors
```

## New UI

Project Model now has:

```text
👥 Actors
```

It can:
- build/refresh Actor Profiles;
- search actors;
- inspect responsibilities;
- inspect owned/related objects;
- inspect process participation;
- inspect interactions;
- inspect permissions;
- inspect evidence.

## Build order

Recommended order:

```text
1. Canonical Facts
2. Entities
3. Relationships
4. Ontology
5. Domain Model
6. Actors
7. Project Summary
```

## Apply

Copy:

```text
models/actor.py
memory/fact_schema.py
repositories/actors_repository.py
builders/actors_builder.py
ui/actors.py
ui/workspace/model.py
repositories/project_repository.py
```

Run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → Actors → Build / Refresh Actors
```

Commit:

```powershell
git add .
git commit -m "Commit 36 - Add actors intelligence layer"
```
