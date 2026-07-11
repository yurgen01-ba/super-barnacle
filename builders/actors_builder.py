from repositories.actors_repository import ActorsRepository
from repositories.domain_model_repository import DomainModelRepository
from repositories.entity_repository import EntityRepository
from repositories.ontology_repository import OntologyRepository
from repositories.relationship_repository import RelationshipRepository


class ActorsBuilder:
    ACTOR_ONTOLOGY_TYPES = {"actor", "role"}

    RESPONSIBILITY_PREDICATES = {
        "creates", "submits", "reviews", "approves", "rejects", "funds", "receives",
        "uploads", "manages", "updates", "uses", "validates", "signs", "pays",
        "repays", "needs_action", "responsible_for",
    }

    OWNERSHIP_PREDICATES = {
        "owns", "has", "created_by", "belongs_to", "assigned_to", "managed_by",
    }

    PROCESS_PREDICATES = {
        "participates_in", "uses", "approves", "reviews", "funds", "pays",
        "repays", "submits", "uploads", "validates",
    }

    PERMISSION_PREDICATES = {
        "can_view", "can_edit", "can_create", "can_delete", "has_access_to",
        "allowed_to", "permission",
    }

    def __init__(self):
        self.actors_repository = ActorsRepository()
        self.domain_repository = DomainModelRepository()
        self.entity_repository = EntityRepository()
        self.ontology_repository = OntologyRepository()
        self.relationship_repository = RelationshipRepository()

    def build_actors(self, limit: int = 5000):
        ontology_rows = self.ontology_repository.list_entity_ontology(limit=limit)
        candidates = [row for row in ontology_rows if row.get("ontology_type") in self.ACTOR_ONTOLOGY_TYPES]

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
                relationships = self.relationship_repository.get_entity_neighborhood(entity.get("name"), limit=250)
                domain_objects = self.domain_repository.list_domain_objects(limit=500)

                actor = self._build_actor_profile(row, entity, facts, relationships, domain_objects)
                self.actors_repository.upsert_actor(**actor)
                built += 1

            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        return {
            "ontology_entities_seen": len(ontology_rows),
            "actor_candidates": len(candidates),
            "actors_built": built,
            "skipped": skipped,
            "stats": self.actors_repository.get_actor_statistics(),
            "errors": errors,
        }

    def _build_actor_profile(self, ontology_row, entity, facts, relationships, domain_objects):
        name = entity.get("name")
        actor_type = self._infer_actor_type(name, relationships)
        responsibilities = self._extract_responsibilities(name, facts, relationships)
        owned_objects = self._extract_owned_objects(name, relationships, domain_objects)
        participates_in = self._extract_participation(name, facts, relationships, domain_objects)
        interactions = self._extract_interactions(name, relationships)
        permissions = self._extract_permissions(facts, relationships)
        evidence = self._extract_evidence(facts, relationships)

        description = self._build_description(
            name, actor_type, entity.get("description"),
            responsibilities, owned_objects, participates_in, interactions,
        )

        confidence = max(float(ontology_row.get("confidence") or 0.3), float(entity.get("confidence") or 0.3))

        return {
            "entity_id": entity["id"],
            "name": name,
            "actor_type": actor_type,
            "description": description,
            "responsibilities": responsibilities,
            "owned_objects": owned_objects,
            "participates_in": participates_in,
            "interactions": interactions,
            "permissions": permissions,
            "evidence": evidence,
            "confidence": confidence,
        }

    def _infer_actor_type(self, name, relationships):
        name_l = (name or "").lower()
        if any(token in name_l for token in ["merchant", "borrower", "client", "customer"]):
            return "external_business_actor"
        if any(token in name_l for token in ["funder", "underwriter", "iso", "isa", "referrer", "syndicator"]):
            return "business_role"
        if any(token in name_l for token in ["admin", "user", "support", "manager"]):
            return "system_user_role"
        if relationships:
            return "project_actor"
        return "unknown_actor"

    def _extract_responsibilities(self, name, facts, relationships):
        items = []
        for fact in facts:
            predicate = fact.get("predicate")
            if predicate in self.RESPONSIBILITY_PREDICATES or fact.get("fact_type") in ("action_item", "requirement", "process"):
                items.append({
                    "statement": f"{fact.get('subject')} → {predicate} → {fact.get('object')}",
                    "predicate": predicate,
                    "target": fact.get("object"),
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                    "evidence": fact.get("evidence"),
                })

        for rel in relationships:
            if rel.get("from_entity_name") == name and rel.get("predicate") in self.RESPONSIBILITY_PREDICATES:
                items.append({
                    "statement": f"{rel.get('from_entity_name')} → {rel.get('predicate')} → {rel.get('to_entity_name')}",
                    "predicate": rel.get("predicate"),
                    "target": rel.get("to_entity_name"),
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                    "evidence": rel.get("evidence"),
                })

        return self._dedupe(items, ["statement", "predicate"])

    def _extract_owned_objects(self, name, relationships, domain_objects):
        domain_names = {item.get("name") for item in domain_objects}
        items = []

        for rel in relationships:
            source = rel.get("from_entity_name")
            target = rel.get("to_entity_name")
            predicate = rel.get("predicate")

            if source == name and (predicate in self.OWNERSHIP_PREDICATES or target in domain_names):
                items.append({
                    "object": target,
                    "predicate": predicate,
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                    "evidence": rel.get("evidence"),
                })

            if target == name and source in domain_names:
                items.append({
                    "object": source,
                    "predicate": predicate,
                    "direction": "incoming",
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                    "evidence": rel.get("evidence"),
                })

        return self._dedupe(items, ["object", "predicate"])

    def _extract_participation(self, name, facts, relationships, domain_objects):
        process_names = {item.get("name") for item in domain_objects if item.get("object_type") in ("process", "workflow")}
        items = []

        for fact in facts:
            if fact.get("predicate") in self.PROCESS_PREDICATES or fact.get("object") in process_names:
                items.append({
                    "process_or_activity": fact.get("object"),
                    "predicate": fact.get("predicate"),
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                })

        for rel in relationships:
            if rel.get("from_entity_name") == name:
                target = rel.get("to_entity_name")
                predicate = rel.get("predicate")
                if target in process_names or predicate in self.PROCESS_PREDICATES:
                    items.append({
                        "process_or_activity": target,
                        "predicate": predicate,
                        "relationship_id": rel.get("id"),
                        "confidence": rel.get("confidence"),
                        "source": rel.get("source"),
                    })

        return self._dedupe(items, ["process_or_activity", "predicate"])

    def _extract_interactions(self, name, relationships):
        items = []
        for rel in relationships:
            source = rel.get("from_entity_name")
            target = rel.get("to_entity_name")
            if source == name:
                items.append({
                    "direction": "outgoing",
                    "with": target,
                    "predicate": rel.get("predicate"),
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                })
            elif target == name:
                items.append({
                    "direction": "incoming",
                    "with": source,
                    "predicate": rel.get("predicate"),
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                })
        return self._dedupe(items, ["direction", "with", "predicate"])

    def _extract_permissions(self, facts, relationships):
        items = []
        for fact in facts:
            if fact.get("predicate") in self.PERMISSION_PREDICATES or fact.get("fact_type") == "permission":
                items.append({
                    "statement": f"{fact.get('subject')} → {fact.get('predicate')} → {fact.get('object')}",
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                })
        for rel in relationships:
            if rel.get("predicate") in self.PERMISSION_PREDICATES:
                items.append({
                    "statement": f"{rel.get('from_entity_name')} → {rel.get('predicate')} → {rel.get('to_entity_name')}",
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                })
        return self._dedupe(items, ["statement"])

    def _extract_evidence(self, facts, relationships):
        evidence = []
        for fact in facts[:50]:
            evidence.append({"type": "fact", "id": fact.get("id"), "source": fact.get("source"), "evidence": fact.get("evidence")})
        for rel in relationships[:50]:
            evidence.append({"type": "relationship", "id": rel.get("id"), "source": rel.get("source"), "evidence": rel.get("evidence")})
        return evidence

    def _build_description(self, name, actor_type, entity_description, responsibilities, owned_objects, participates_in, interactions):
        parts = [f"{name} is classified as {actor_type}."]
        if entity_description:
            parts.append(entity_description)
        if responsibilities:
            parts.append(f"Known responsibilities: {len(responsibilities)}.")
        if owned_objects:
            parts.append(f"Related/owned business objects: {', '.join(str(item.get('object')) for item in owned_objects[:8])}.")
        if participates_in:
            parts.append(f"Participates in: {', '.join(str(item.get('process_or_activity')) for item in participates_in[:8])}.")
        if interactions:
            parts.append(f"Known interactions: {len(interactions)}.")
        return " ".join(parts)

    def _dedupe(self, items, key_fields):
        seen = set()
        result = []
        for item in items:
            key = tuple(str(item.get(field) or "").lower() for field in key_fields)
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

