from repositories.entity_repository import EntityRepository
from repositories.fact_repository import FactRepository
from repositories.relationship_repository import RelationshipRepository


class RelationshipBuilder:
    """
    Builds entity relationships from Canonical Facts.

    It uses facts in the form:

        subject → predicate → object

    and connects existing/new entities:

        Entity(subject) --predicate--> Entity(object)

    This is the first graph layer of Project Brain.
    """

    NON_RELATIONAL_PREDICATES = {
        "has_field",
        "has_value",
        "has_description",
        "has_title",
        "has_note",
        "has_comment",
    }

    GENERIC_OBJECTS = {
        "yes",
        "no",
        "true",
        "false",
        "unknown",
        "required",
        "optional",
        "high",
        "medium",
        "low",
        "open",
        "closed",
    }

    def __init__(self):
        self.fact_repository = FactRepository()
        self.entity_repository = EntityRepository()
        self.relationship_repository = RelationshipRepository()

    def build_relationships_from_facts(self, limit: int = 5000):
        facts = self.fact_repository.list_facts(limit=limit)

        created_or_updated = 0
        skipped = 0
        errors = []

        for fact in facts:
            try:
                subject = self._clean_entity_name(fact.get("subject"))
                predicate = (fact.get("predicate") or "").strip()
                obj = self._clean_entity_name(fact.get("object"))

                if not self._is_relationship_candidate(subject, predicate, obj):
                    skipped += 1
                    continue

                from_entity_id = self._ensure_entity(subject, fact)
                to_entity_id = self._ensure_entity(obj, fact, as_object=True)

                if not from_entity_id or not to_entity_id:
                    skipped += 1
                    continue

                relationship_id = self.relationship_repository.upsert_relationship(
                    from_entity_id=from_entity_id,
                    to_entity_id=to_entity_id,
                    predicate=predicate,
                    fact_id=fact.get("id"),
                    confidence=fact.get("confidence") or 0.7,
                    evidence=fact.get("evidence"),
                    source=fact.get("source"),
                    metadata={
                        "fact_type": fact.get("fact_type"),
                        "status": fact.get("status"),
                        "builder": "relationship_builder_v1",
                    },
                )

                if relationship_id:
                    created_or_updated += 1

            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        relationships_total = len(self.relationship_repository.list_relationships(limit=100000))

        return {
            "facts_processed": len(facts),
            "relationships_total": relationships_total,
            "created_or_updated": created_or_updated,
            "skipped": skipped,
            "errors": errors,
        }

    def _is_relationship_candidate(self, subject: str, predicate: str, obj: str):
        if not subject or not predicate or not obj:
            return False

        if predicate in self.NON_RELATIONAL_PREDICATES:
            return False

        if obj.lower() in self.GENERIC_OBJECTS:
            return False

        if obj.isdigit():
            return False

        if len(obj) > 100:
            return False

        if subject.lower() == obj.lower():
            return False

        return True

    def _ensure_entity(self, name: str, fact: dict, as_object: bool = False):
        existing = self.entity_repository.get_entity_by_name(name)

        if existing:
            return existing["id"]

        entity_type = "related_object" if as_object else "unknown"

        return self.entity_repository.upsert_entity(
            name=name,
            entity_type=entity_type,
            description=f"Entity auto-created from relationship fact #{fact.get('id')}.",
            metadata={
                "created_by": "relationship_builder",
                "fact_id": fact.get("id"),
            },
            confidence=fact.get("confidence") or 0.7,
        )

    def _clean_entity_name(self, value):
        value = str(value or "").strip()
        value = value.strip(" .,:;!?()[]{}\"'")

        if not value or len(value) > 120:
            return ""

        return value

