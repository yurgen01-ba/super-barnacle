from repositories.domain_model_repository import DomainModelRepository
from repositories.entity_repository import EntityRepository
from repositories.ontology_repository import OntologyRepository
from repositories.relationship_repository import RelationshipRepository


class DomainModelBuilder:
    """
    Builds a DDD-like Domain Model from Ontology, Entities, Facts, and Relationships.

    Commit 35 scope:
    - converts business_object/data_object/product/module/process-like entities into domain objects;
    - collects attributes from has_field / has_status / has_value / can_have_status facts;
    - collects business rules and requirements;
    - collects relationships and lifecycle hints;
    - stores structured JSON per domain object.
    """

    DOMAIN_ONTOLOGY_TYPES = {
        "business_object",
        "data_object",
        "product",
        "module",
        "process",
        "workflow",
        "document",
        "screen",
        "report",
        "configuration",
        "status",
        "metric",
    }

    ATTRIBUTE_PREDICATES = {
        "has_field",
        "has_attribute",
        "has_status",
        "can_have_status",
        "has_value",
        "stores",
        "contains",
        "includes",
    }

    LIFECYCLE_PREDICATES = {
        "has_status",
        "can_have_status",
        "transitions_to",
        "happens_after",
        "starts_with",
        "ends_with",
        "completed_by",
        "approved_by",
        "rejected_by",
    }

    RULE_FACT_TYPES = {
        "business_rule",
        "requirement",
        "constraint",
        "risk",
        "question",
        "assumption",
    }

    def __init__(self):
        self.domain_repository = DomainModelRepository()
        self.entity_repository = EntityRepository()
        self.ontology_repository = OntologyRepository()
        self.relationship_repository = RelationshipRepository()

    def build_domain_model(self, limit: int = 5000):
        ontology_rows = self.ontology_repository.list_entity_ontology(limit=limit)

        candidates = [
            row for row in ontology_rows
            if row.get("ontology_type") in self.DOMAIN_ONTOLOGY_TYPES
        ]

        built = 0
        skipped = 0
        errors = []

        for row in candidates:
            try:
                entity_id = row["entity_id"]
                profile = self.entity_repository.build_entity_profile(entity_id)

                if not profile:
                    skipped += 1
                    continue

                entity = profile["entity"]
                facts = profile.get("facts", [])
                relationships = self.relationship_repository.get_entity_neighborhood(
                    entity.get("name"),
                    limit=200,
                )

                domain_object = self._build_domain_object(
                    ontology_row=row,
                    entity=entity,
                    facts=facts,
                    relationships=relationships,
                )

                self.domain_repository.upsert_domain_object(**domain_object)
                built += 1

            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        return {
            "ontology_entities_seen": len(ontology_rows),
            "domain_candidates": len(candidates),
            "domain_objects_built": built,
            "skipped": skipped,
            "stats": self.domain_repository.get_domain_model_statistics(),
            "errors": errors,
        }

    def _build_domain_object(self, ontology_row: dict, entity: dict, facts: list[dict], relationships: list[dict]):
        name = entity.get("name")
        ontology_type = ontology_row.get("ontology_type") or "business_object"

        attributes = self._extract_attributes(facts)
        rules = self._extract_rules(facts)
        lifecycle = self._extract_lifecycle(facts, relationships)
        relationship_items = self._extract_relationships(name, relationships)
        evidence = self._extract_evidence(facts, relationships)

        description = self._build_description(
            name=name,
            ontology_type=ontology_type,
            entity_description=entity.get("description"),
            attributes=attributes,
            relationships=relationship_items,
            rules=rules,
        )

        confidence = max(
            float(ontology_row.get("confidence") or 0.3),
            float(entity.get("confidence") or 0.3),
        )

        return {
            "entity_id": entity["id"],
            "name": name,
            "description": description,
            "object_type": ontology_type,
            "attributes": attributes,
            "relationships": relationship_items,
            "rules": rules,
            "lifecycle": lifecycle,
            "evidence": evidence,
            "confidence": confidence,
        }

    def _extract_attributes(self, facts: list[dict]):
        result = []

        for fact in facts:
            predicate = fact.get("predicate")

            if predicate not in self.ATTRIBUTE_PREDICATES:
                continue

            result.append({
                "name": fact.get("object"),
                "predicate": predicate,
                "fact_id": fact.get("id"),
                "confidence": fact.get("confidence"),
                "source": fact.get("source"),
                "evidence": fact.get("evidence"),
            })

        return self._dedupe_dicts(result, key_fields=["name", "predicate"])

    def _extract_rules(self, facts: list[dict]):
        result = []

        for fact in facts:
            if fact.get("fact_type") not in self.RULE_FACT_TYPES:
                continue

            result.append({
                "type": fact.get("fact_type"),
                "statement": f"{fact.get('subject')} → {fact.get('predicate')} → {fact.get('object')}",
                "fact_id": fact.get("id"),
                "confidence": fact.get("confidence"),
                "source": fact.get("source"),
                "evidence": fact.get("evidence"),
            })

        return self._dedupe_dicts(result, key_fields=["statement", "type"])

    def _extract_lifecycle(self, facts: list[dict], relationships: list[dict]):
        result = []

        for fact in facts:
            if fact.get("predicate") in self.LIFECYCLE_PREDICATES:
                result.append({
                    "step_or_state": fact.get("object"),
                    "predicate": fact.get("predicate"),
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                })

        for rel in relationships:
            if rel.get("predicate") in self.LIFECYCLE_PREDICATES:
                result.append({
                    "step_or_state": rel.get("to_entity_name"),
                    "predicate": rel.get("predicate"),
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                })

        return self._dedupe_dicts(result, key_fields=["step_or_state", "predicate"])

    def _extract_relationships(self, name: str, relationships: list[dict]):
        result = []

        for rel in relationships:
            if rel.get("from_entity_name") == name:
                direction = "outgoing"
                related = rel.get("to_entity_name")
            elif rel.get("to_entity_name") == name:
                direction = "incoming"
                related = rel.get("from_entity_name")
            else:
                continue

            result.append({
                "direction": direction,
                "predicate": rel.get("predicate"),
                "related_object": related,
                "relationship_id": rel.get("id"),
                "fact_id": rel.get("fact_id"),
                "confidence": rel.get("confidence"),
                "source": rel.get("source"),
                "evidence": rel.get("evidence"),
            })

        return self._dedupe_dicts(result, key_fields=["direction", "predicate", "related_object"])

    def _extract_evidence(self, facts: list[dict], relationships: list[dict]):
        evidence = []

        for fact in facts[:50]:
            evidence.append({
                "type": "fact",
                "id": fact.get("id"),
                "source": fact.get("source"),
                "evidence": fact.get("evidence"),
            })

        for rel in relationships[:30]:
            evidence.append({
                "type": "relationship",
                "id": rel.get("id"),
                "source": rel.get("source"),
                "evidence": rel.get("evidence"),
            })

        return evidence

    def _build_description(self, name, ontology_type, entity_description, attributes, relationships, rules):
        parts = [
            f"{name} is classified as {ontology_type}.",
        ]

        if entity_description:
            parts.append(entity_description)

        if attributes:
            parts.append(f"Known attributes/states: {', '.join(str(item.get('name')) for item in attributes[:8])}.")

        if relationships:
            parts.append(f"Known relationships: {len(relationships)}.")

        if rules:
            parts.append(f"Known rules/requirements/risks: {len(rules)}.")

        return " ".join(parts)

    def _dedupe_dicts(self, items: list[dict], key_fields: list[str]):
        seen = set()
        result = []

        for item in items:
            key = tuple(str(item.get(field) or "").lower() for field in key_fields)

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result

