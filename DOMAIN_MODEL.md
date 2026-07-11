# Project Brain Domain Model

## Project

A Project is the top-level workspace.

A Project contains:

```text
Sources
Knowledge Nodes
Relationships
Artifacts
Settings
Users
Project Model
```

## Knowledge Node

A Knowledge Node is the universal unit of project knowledge.

Common fields:

```text
id
project_id
node_type
title
description
status
confidence
source_refs
metadata
created_at
updated_at
version
```

Node types:

```text
Source
Source Fragment
Fact
Entity
Actor
Process
Process Step
Business Rule
Requirement
Decision
Risk
Integration
API
Screen
Database Table
Metric
Artifact
Glossary Term
Timeline Event
Hypothesis
```

## Relationship

A Relationship connects two Knowledge Nodes.

Common fields:

```text
id
project_id
from_node_id
to_node_id
relationship_type
confidence
evidence_refs
metadata
created_at
updated_at
```

Relationship types:

```text
relates_to
depends_on
participates_in
owns
uses
creates
updates
implements
documents
tests
affects
contradicts
supersedes
discussed_in
derived_from
belongs_to
owned_by
```

## Evidence

Evidence explains why a node or relationship exists.

Evidence can point to:

```text
Meeting timestamp
Transcript chunk
Screen frame
Slack message
Jira ticket
Confluence page
PDF page
Manual user note
```

## Status

Knowledge should have lifecycle status:

```text
proposed
active
deprecated
conflict
rejected
unknown
```

## Confidence

Confidence represents how reliable the knowledge is.

Initial confidence can depend on source type:

```text
Confluence: high
Jira: high
Meeting transcript: medium
Screen observation: medium
Slack: low/medium
LLM inference: low unless supported by evidence
Manual confirmation: very high
```

## Current existing objects

The current system already has:

```text
Knowledge Items
Facts
Entities
Relationships
Ontology
Domain Objects
Actors
Processes
Project Summary
Sources
Jobs
```

These should gradually converge into the Knowledge Node model.
