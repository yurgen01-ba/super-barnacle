from collections import Counter, defaultdict

from repositories.entity_repository import EntityRepository
from repositories.fact_repository import FactRepository


class EntityBuilder:
    """
    Builds first-class entities from Canonical Facts.

    Commit 29 scope:
    - create/upsert entity for each fact subject;
    - optionally create/upsert entity for object when object looks like a domain noun;
    - link facts to entities as subject/object/about;
    - infer simple entity type;
    - store lightweight metadata.
    """

    GENERIC_OBJECTS = {
        "yes",
        "no",
        "true",
        "false",
        "unknown",
        "open",
        "closed",
        "pending",
        "approved",
        "rejected",
        "required",
        "optional",
        "high",
        "medium",
        "low",
    }

    ENTITY_TYPE_HINTS = {
        "merchant": "business_object",
        "advance": "business_object",
        "funder": "role",
        "underwriter": "role",
        "syndicator": "role",
        "isa": "role",
        "referrer": "role",
        "loc": "product",
        "loci": "product",
        "rdmetr": "product",
        "worksheet": "business_object",
        "payment": "business_object",
        "payback": "process",
        "funding": "process",
        "underwriting": "process",
        "collection": "process",
        "collections": "process",
        "plaid": "integration",
        "stripe": "integration",
        "api": "technical_object",
    }

    PROCESS_PREDICATES = {
        "requires",
        "depends_on",
        "happens_after",
        "blocks",
        "validates",
        "produces",
        "uses",
        "stores",
        "integrates_with",
        "approved_by",
        "funded_by",
        "created_by",
    }

    def __init__(self):
        self.fact_repository = FactRepository()
        self.entity_repository = EntityRepository()

    def build_entities_from_facts(self, limit: int = 5000):
        facts = self.fact_repository.list_facts(limit=limit)

        created_or_updated = 0
        links_created = 0
        skipped = 0
        errors = []

        subject_counter = Counter()
        object_counter = Counter()
        fact_type_counter = defaultdict(Counter)

        for fact in facts:
            try:
                subject = self._clean_entity_name(fact.get("subject"))
                obj = self._clean_entity_name(fact.get("object"))

                if not subject:
                    skipped += 1
                    continue

                subject_counter[subject] += 1
                fact_type_counter[subject][fact.get("fact_type") or "unknown"] += 1

                subject_entity_id = self.entity_repository.upsert_entity(
                    name=subject,
                    entity_type=self._infer_entity_type(subject, fact),
                    description=self._make_entity_description(subject, fact),
                    metadata={
                        "last_fact_id": fact.get("id"),
                        "last_predicate": fact.get("predicate"),
                        "build_source": "canonical_facts",
                    },
                    confidence=fact.get("confidence") or 0.7,
                )

                if subject_entity_id:
                    created_or_updated += 1
                    self.entity_repository.link_fact(
                        entity_id=subject_entity_id,
                        fact_id=fact["id"],
                        relation_type="subject",
                    )
                    links_created += 1

                if self._looks_like_entity_object(obj):
                    object_counter[obj] += 1
                    fact_type_counter[obj][fact.get("fact_type") or "unknown"] += 1

                    object_entity_id = self.entity_repository.upsert_entity(
                        name=obj,
                        entity_type=self._infer_entity_type(obj, fact, as_object=True),
                        description=self._make_entity_description(obj, fact),
                        metadata={
                            "last_fact_id": fact.get("id"),
                            "mentioned_as_object_of": fact.get("subject"),
                            "last_predicate": fact.get("predicate"),
                            "build_source": "canonical_facts",
                        },
                        confidence=fact.get("confidence") or 0.7,
                    )

                    if object_entity_id:
                        created_or_updated += 1
                        self.entity_repository.link_fact(
                            entity_id=object_entity_id,
                            fact_id=fact["id"],
                            relation_type="object",
                        )
                        links_created += 1

            except Exception as exc:
                skipped += 1
                errors.append(repr(exc))

        entities = self.entity_repository.list_entities(limit=10000)

        return {
            "facts_processed": len(facts),
            "entities_total": len(entities),
            "created_or_updated": created_or_updated,
            "links_created": links_created,
            "skipped": skipped,
            "errors": errors,
            "top_subjects": subject_counter.most_common(20),
            "top_objects": object_counter.most_common(20),
        }

    def _clean_entity_name(self, value):
        value = str(value or "").strip()

        if not value:
            return ""

        value = value.strip(" .,:;!?()[]{}\"'")

        if len(value) > 120:
            return ""

        return value

    def _looks_like_entity_object(self, value: str):
        if not value:
            return False

        if len(value) < 2 or len(value) > 80:
            return False

        if value.lower() in self.GENERIC_OBJECTS:
            return False

        if value.isdigit():
            return False

        # Domain objects usually start with upper-case or contain meaningful words.
        if value[0].isupper():
            return True

        if "_" in value or " " in value:
            return len(value.split()) <= 5

        return value.lower() in self.ENTITY_TYPE_HINTS

    def _infer_entity_type(self, name: str, fact: dict, as_object: bool = False):
        lower_name = (name or "").lower()
        predicate = (fact.get("predicate") or "").lower()
        fact_type = (fact.get("fact_type") or "").lower()

        for hint, entity_type in self.ENTITY_TYPE_HINTS.items():
            if hint in lower_name:
                return entity_type

        if fact_type == "integration":
            return "integration"

        if fact_type == "api":
            return "technical_object"

        if fact_type in ("ui_screen",):
            return "ui"

        if fact_type in ("process", "workflow"):
            return "process"

        if predicate in self.PROCESS_PREDICATES and as_object:
            return "related_object"

        return "unknown"

    def _make_entity_description(self, name: str, fact: dict):
        fact_type = fact.get("fact_type") or "unknown"
        predicate = fact.get("predicate") or "relates_to"
        subject = fact.get("subject") or ""
        obj = fact.get("object") or ""

        if name == subject:
            return f"Entity inferred from canonical facts. Latest relation: {subject} → {predicate} → {obj} ({fact_type})."

        return f"Entity inferred as object from canonical facts. Latest relation: {subject} → {predicate} → {obj} ({fact_type})."

