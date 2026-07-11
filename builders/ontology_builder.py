from core.ontology import infer_ontology_type_heuristic
from repositories.entity_repository import EntityRepository
from repositories.ontology_repository import OntologyRepository


class OntologyBuilder:
    def __init__(self):
        self.entity_repository = EntityRepository()
        self.ontology_repository = OntologyRepository()

    def classify_entities(self, limit: int = 5000):
        entities = self.entity_repository.list_entities(limit=limit)

        classified = 0
        unknown = 0
        errors = []

        for entity in entities:
            try:
                profile = self.entity_repository.build_entity_profile(entity["id"])
                facts = profile.get("facts", []) if profile else []

                ontology_type, confidence, reason = infer_ontology_type_heuristic(
                    name=entity.get("name"),
                    entity_type=entity.get("entity_type"),
                    facts=facts,
                )

                self.ontology_repository.upsert_entity_ontology(
                    entity_id=entity["id"],
                    ontology_type=ontology_type,
                    confidence=confidence,
                    classification_method="heuristic_v1",
                    reason=reason,
                    metadata={
                        "entity_name": entity.get("name"),
                        "entity_type": entity.get("entity_type"),
                        "facts_count": len(facts),
                    },
                )

                classified += 1

                if ontology_type == "unknown":
                    unknown += 1

            except Exception as exc:
                errors.append(repr(exc))

        return {
            "entities_processed": len(entities),
            "classified": classified,
            "unknown": unknown,
            "counts": self.ontology_repository.get_ontology_counts(),
            "errors": errors,
        }

