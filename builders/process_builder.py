from collections import defaultdict

from repositories.actors_repository import ActorsRepository
from repositories.domain_model_repository import DomainModelRepository
from repositories.fact_repository import FactRepository
from repositories.process_repository import ProcessRepository
from repositories.relationship_repository import RelationshipRepository


class ProcessBuilder:
    """
    Builds Business Process Intelligence from Domain Model, Actors,
    Relationships and Canonical Facts.

    This builder is deterministic and idempotent: repeated runs update the same
    process records by name instead of creating duplicates.
    """

    PROCESS_OBJECT_TYPES = {"process", "workflow"}
    PROCESS_FACT_TYPES = {"process", "workflow", "business_rule", "requirement", "constraint", "risk", "question"}

    STEP_PREDICATES = {
        "starts_with", "ends_with", "happens_after", "happens_before", "transitions_to",
        "requires", "depends_on", "blocks", "triggers", "produces", "creates",
        "submits", "reviews", "approves", "rejects", "funds", "pays", "repays",
        "validates", "uploads", "uses", "stores", "sends", "receives",
    }

    INPUT_PREDICATES = {"requires", "uses", "depends_on", "reads", "loads", "imports", "uploads"}
    OUTPUT_PREDICATES = {"produces", "creates", "generates", "sends", "exports", "stores"}
    EXCEPTION_FACT_TYPES = {"risk", "question", "bug"}
    RULE_FACT_TYPES = {"business_rule", "requirement", "constraint", "assumption"}

    def __init__(self):
        self.process_repository = ProcessRepository()
        self.domain_repository = DomainModelRepository()
        self.actors_repository = ActorsRepository()
        self.relationship_repository = RelationshipRepository()
        self.fact_repository = FactRepository()

    def build_processes(self, limit: int = 5000):
        domain_objects = self.domain_repository.list_domain_objects(limit=limit)
        actors = self.actors_repository.list_actors(limit=limit)
        facts = self.fact_repository.list_facts(limit=limit)
        relationships = self.relationship_repository.list_relationships(limit=limit)

        process_names = self._discover_process_names(domain_objects, facts, relationships)
        built = 0
        skipped = 0
        errors = []

        for process_name in sorted(process_names):
            try:
                profile = self._build_process_profile(
                    process_name=process_name,
                    domain_objects=domain_objects,
                    actors=actors,
                    facts=facts,
                    relationships=relationships,
                )
                if not profile:
                    skipped += 1
                    continue
                self.process_repository.upsert_process(**profile)
                built += 1
            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        return {
            "process_candidates": len(process_names),
            "processes_built": built,
            "skipped": skipped,
            "stats": self.process_repository.get_process_statistics(),
            "errors": errors,
        }

    def _discover_process_names(self, domain_objects, facts, relationships):
        names = set()

        for item in domain_objects:
            if item.get("object_type") in self.PROCESS_OBJECT_TYPES:
                names.add(item.get("name"))

        for fact in facts:
            if fact.get("fact_type") in ("process", "workflow"):
                names.add(fact.get("subject"))
                if self._looks_like_process_name(fact.get("object")):
                    names.add(fact.get("object"))
            if self._looks_like_process_name(fact.get("subject")):
                names.add(fact.get("subject"))
            if fact.get("predicate") in ("participates_in", "happens_after", "starts_with", "ends_with"):
                if self._looks_like_process_name(fact.get("object")):
                    names.add(fact.get("object"))

        for rel in relationships:
            for value in (rel.get("from_entity_name"), rel.get("to_entity_name")):
                if self._looks_like_process_name(value):
                    names.add(value)

        return {name.strip() for name in names if name and len(str(name).strip()) <= 120}

    def _looks_like_process_name(self, value):
        value = str(value or "").strip().lower()
        if not value:
            return False
        hints = [
            "process", "workflow", "flow", "lifecycle", "pipeline", "application", "onboarding",
            "underwriting", "approval", "funding", "repayment", "payback", "collection",
            "collections", "reconciliation", "settlement", "export", "import", "review",
        ]
        return any(hint in value for hint in hints)

    def _build_process_profile(self, process_name, domain_objects, actors, facts, relationships):
        related_facts = self._filter_related_facts(process_name, facts)
        related_relationships = self._filter_related_relationships(process_name, relationships)

        if not related_facts and not related_relationships:
            return None

        participants = self._extract_participants(process_name, actors, related_facts, related_relationships)
        business_objects = self._extract_business_objects(process_name, domain_objects, related_facts, related_relationships)
        steps = self._extract_steps(process_name, related_facts, related_relationships)
        inputs = self._extract_io(related_facts, related_relationships, self.INPUT_PREDICATES, direction="input")
        outputs = self._extract_io(related_facts, related_relationships, self.OUTPUT_PREDICATES, direction="output")
        rules = self._extract_rules(related_facts)
        exceptions = self._extract_exceptions(related_facts)
        evidence = self._extract_evidence(related_facts, related_relationships)
        goal = self._infer_goal(process_name, steps, outputs)
        description = self._build_description(process_name, participants, business_objects, steps, rules, exceptions)
        confidence = self._calculate_confidence(related_facts, related_relationships, participants, business_objects, steps)

        return {
            "name": process_name,
            "description": description,
            "process_type": "business_process",
            "goal": goal,
            "participants": participants,
            "business_objects": business_objects,
            "steps": steps,
            "inputs": inputs,
            "outputs": outputs,
            "rules": rules,
            "exceptions": exceptions,
            "evidence": evidence,
            "confidence": confidence,
        }

    def _filter_related_facts(self, process_name, facts):
        key = process_name.lower()
        result = []
        for fact in facts:
            text = " ".join([
                str(fact.get("subject") or ""),
                str(fact.get("predicate") or ""),
                str(fact.get("object") or ""),
                str(fact.get("fact_type") or ""),
            ]).lower()
            if key in text or (fact.get("fact_type") in self.PROCESS_FACT_TYPES and self._loosely_related(key, text)):
                result.append(fact)
        return result[:300]

    def _filter_related_relationships(self, process_name, relationships):
        key = process_name.lower()
        result = []
        for rel in relationships:
            text = " ".join([
                str(rel.get("from_entity_name") or ""),
                str(rel.get("predicate") or ""),
                str(rel.get("to_entity_name") or ""),
            ]).lower()
            if key in text:
                result.append(rel)
        return result[:300]

    def _loosely_related(self, key, text):
        tokens = [token for token in key.replace("_", " ").split() if len(token) >= 4]
        return bool(tokens and any(token in text for token in tokens))

    def _extract_participants(self, process_name, actors, facts, relationships):
        actor_names = {actor.get("name") for actor in actors}
        result = []

        for actor in actors:
            actor_name = actor.get("name")
            actor_text = " ".join([
                actor_name or "",
                str(actor.get("description") or ""),
                str(actor.get("participates_in") or ""),
                str(actor.get("responsibilities") or ""),
            ]).lower()
            if process_name.lower() in actor_text:
                result.append({
                    "actor": actor_name,
                    "actor_type": actor.get("actor_type"),
                    "source": "actor_profile",
                    "confidence": actor.get("confidence"),
                })

        for rel in relationships:
            source = rel.get("from_entity_name")
            target = rel.get("to_entity_name")
            if source in actor_names:
                result.append({"actor": source, "role": rel.get("predicate"), "target": target, "relationship_id": rel.get("id"), "confidence": rel.get("confidence")})
            if target in actor_names:
                result.append({"actor": target, "role": rel.get("predicate"), "target": source, "relationship_id": rel.get("id"), "confidence": rel.get("confidence")})

        for fact in facts:
            if fact.get("subject") in actor_names:
                result.append({"actor": fact.get("subject"), "role": fact.get("predicate"), "target": fact.get("object"), "fact_id": fact.get("id"), "confidence": fact.get("confidence")})

        return self._dedupe(result, ["actor", "role", "target"])

    def _extract_business_objects(self, process_name, domain_objects, facts, relationships):
        domain_names = {item.get("name") for item in domain_objects}
        result = []

        for obj in domain_objects:
            obj_name = obj.get("name")
            obj_text = " ".join([obj_name or "", str(obj.get("description") or ""), str(obj.get("relationships") or ""), str(obj.get("rules") or "")]).lower()
            if process_name.lower() in obj_text:
                result.append({"object": obj_name, "object_type": obj.get("object_type"), "source": "domain_model", "confidence": obj.get("confidence")})

        for rel in relationships:
            for candidate in [rel.get("from_entity_name"), rel.get("to_entity_name")]:
                if candidate in domain_names:
                    result.append({"object": candidate, "predicate": rel.get("predicate"), "relationship_id": rel.get("id"), "confidence": rel.get("confidence")})

        for fact in facts:
            for candidate in [fact.get("subject"), fact.get("object")]:
                if candidate in domain_names:
                    result.append({"object": candidate, "predicate": fact.get("predicate"), "fact_id": fact.get("id"), "confidence": fact.get("confidence")})

        return self._dedupe(result, ["object", "predicate"])

    def _extract_steps(self, process_name, facts, relationships):
        result = []
        order = 1

        for rel in relationships:
            predicate = rel.get("predicate")
            if predicate in self.STEP_PREDICATES:
                result.append({
                    "order": order,
                    "step": f"{rel.get('from_entity_name')} {predicate} {rel.get('to_entity_name')}",
                    "predicate": predicate,
                    "from": rel.get("from_entity_name"),
                    "to": rel.get("to_entity_name"),
                    "relationship_id": rel.get("id"),
                    "confidence": rel.get("confidence"),
                })
                order += 1

        for fact in facts:
            predicate = fact.get("predicate")
            if predicate in self.STEP_PREDICATES or fact.get("fact_type") in ("process", "workflow", "action_item"):
                result.append({
                    "order": order,
                    "step": f"{fact.get('subject')} {predicate} {fact.get('object')}",
                    "predicate": predicate,
                    "from": fact.get("subject"),
                    "to": fact.get("object"),
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                })
                order += 1

        return self._dedupe(result, ["step", "predicate"])

    def _extract_io(self, facts, relationships, predicates, direction):
        result = []
        for fact in facts:
            if fact.get("predicate") in predicates:
                result.append({"name": fact.get("object"), "predicate": fact.get("predicate"), "direction": direction, "fact_id": fact.get("id"), "confidence": fact.get("confidence")})
        for rel in relationships:
            if rel.get("predicate") in predicates:
                result.append({"name": rel.get("to_entity_name"), "predicate": rel.get("predicate"), "direction": direction, "relationship_id": rel.get("id"), "confidence": rel.get("confidence")})
        return self._dedupe(result, ["name", "predicate", "direction"])

    def _extract_rules(self, facts):
        result = []
        for fact in facts:
            if fact.get("fact_type") in self.RULE_FACT_TYPES:
                result.append({
                    "type": fact.get("fact_type"),
                    "statement": f"{fact.get('subject')} → {fact.get('predicate')} → {fact.get('object')}",
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                    "evidence": fact.get("evidence"),
                })
        return self._dedupe(result, ["statement", "type"])

    def _extract_exceptions(self, facts):
        result = []
        for fact in facts:
            if fact.get("fact_type") in self.EXCEPTION_FACT_TYPES:
                result.append({
                    "type": fact.get("fact_type"),
                    "statement": f"{fact.get('subject')} → {fact.get('predicate')} → {fact.get('object')}",
                    "fact_id": fact.get("id"),
                    "confidence": fact.get("confidence"),
                    "source": fact.get("source"),
                })
        return self._dedupe(result, ["statement", "type"])

    def _extract_evidence(self, facts, relationships):
        evidence = []
        for fact in facts[:80]:
            evidence.append({"type": "fact", "id": fact.get("id"), "source": fact.get("source"), "evidence": fact.get("evidence")})
        for rel in relationships[:80]:
            evidence.append({"type": "relationship", "id": rel.get("id"), "source": rel.get("source"), "evidence": rel.get("evidence")})
        return evidence

    def _infer_goal(self, process_name, steps, outputs):
        if outputs:
            return f"Produce or update {', '.join(str(item.get('name')) for item in outputs[:5])}."
        if steps:
            return f"Coordinate {len(steps)} known step(s) related to {process_name}."
        return f"Describe and control the {process_name} process."

    def _build_description(self, process_name, participants, business_objects, steps, rules, exceptions):
        parts = [f"{process_name} is a business process inferred from the Project Model."]
        if participants:
            parts.append(f"Known participants: {', '.join(str(item.get('actor')) for item in participants[:8])}.")
        if business_objects:
            parts.append(f"Related business objects: {', '.join(str(item.get('object')) for item in business_objects[:8])}.")
        if steps:
            parts.append(f"Known steps: {len(steps)}.")
        if rules:
            parts.append(f"Known rules/requirements: {len(rules)}.")
        if exceptions:
            parts.append(f"Known risks/open questions/exceptions: {len(exceptions)}.")
        return " ".join(parts)

    def _calculate_confidence(self, facts, relationships, participants, business_objects, steps):
        score = 0.25
        score += min(len(facts), 20) * 0.015
        score += min(len(relationships), 20) * 0.015
        score += min(len(participants), 8) * 0.025
        score += min(len(business_objects), 8) * 0.02
        score += min(len(steps), 10) * 0.025
        return round(min(score, 0.98), 2)

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

