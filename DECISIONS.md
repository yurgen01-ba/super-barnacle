# Architecture and Product Decisions

## Decision 001 — Project Brain is not a chatbot

Date: 2026-07-07

Project Brain should be designed as a Project Knowledge Graph with an AI reasoning layer.

Reason: chat alone cannot provide reliable project understanding.

## Decision 002 — AI Assistant is always available

Date: 2026-07-07

AI Assistant should not be a separate page. It should be available in the workspace as a persistent side panel or equivalent always-available interaction surface.

Reason: the assistant is a working companion, not a separate destination.

## Decision 003 — Artifacts belong to AI Assistant

Date: 2026-07-07

Artifact generation should be accessible from the AI Assistant.

Reason: artifacts are usually created as a result of conversation and analysis.

## Decision 004 — Dashboard contains ingestion

Date: 2026-07-07

Data upload/import must be available directly from the Dashboard.

Reason: the first user action is often to add new project information.

## Decision 005 — Project Model is an advanced mode

Date: 2026-07-07

Project Model should not be a primary menu item for normal users.

Reason: Facts, Entities, Ontology, Relationships and internal model views are useful for power users and development, but too technical for the main workflow.

## Decision 006 — Multi-project support is foundational

Date: 2026-07-07

The product should assume multiple projects from the beginning.

Reason: project separation is required for memory, permissions, artifacts and knowledge graph isolation.

## Decision 007 — UI v2 remains Streamlit for now

Date: 2026-07-07

Do not migrate to React/FastAPI yet.

Reason: the core intelligence model is still evolving.

## Decision 008 — Knowledge Graph is the next core milestone

Date: 2026-07-07

The next major technical milestone is Project Knowledge Graph Engine.

Reason: a unified Knowledge Graph is needed for reasoning, traceability and impact analysis.
