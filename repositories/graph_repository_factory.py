from __future__ import annotations

from typing import Any

from graph.graph_builder import GraphBuilder
from graph.graph_repository import GraphRepository


REPOSITORY_CANDIDATES = {
    "fact_repository": [
        "repositories.fact_repository.FactRepository",
        "repositories.memory_repository.MemoryRepository",
    ],
    "entity_repository": [
        "repositories.entity_repository.EntityRepository",
    ],
    "actor_repository": [
        "repositories.actors_repository.ActorsRepository",
        "repositories.actors_repository.ActorRepository",
    ],
    "process_repository": [
        "repositories.process_repository.ProcessRepository",
    ],
    "relationship_repository": [
        "repositories.relationship_repository.RelationshipRepository",
    ],
    "domain_model_repository": [
        "repositories.domain_model_repository.DomainModelRepository",
    ],
    "ontology_repository": [
        "repositories.ontology_repository.OntologyRepository",
    ],
}


def safe_init(class_path: str):
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls()
    except Exception:
        return None


def init_first_available(candidates: list[str]):
    for candidate in candidates:
        instance = safe_init(candidate)
        if instance is not None:
            return instance
    return None


def build_default_graph_repositories() -> dict[str, Any]:
    return {
        key: init_first_available(candidates)
        for key, candidates in REPOSITORY_CANDIDATES.items()
    }


def build_default_graph_repository() -> GraphRepository:
    repositories = build_default_graph_repositories()
    builder = GraphBuilder(**repositories)
    return GraphRepository(builder=builder)
