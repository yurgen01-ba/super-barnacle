from providers.text.factory import create_text_provider
from repositories.actors_repository import ActorsRepository
from repositories.domain_model_repository import DomainModelRepository
from repositories.entity_repository import EntityRepository
from repositories.fact_repository import FactRepository
from repositories.ontology_repository import OntologyRepository
from repositories.process_repository import ProcessRepository
from repositories.project_repository import ProjectRepository
from repositories.relationship_repository import RelationshipRepository


class ProjectSummaryBuilder:
    """
    Builds Project Summary from Project Intelligence layers:
    - Canonical Facts
    - Entities / Ontology / Relationships
    - Domain Model
    - Actors
    - Processes
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        host: str = "http://localhost:11434",
        timeout_seconds: int = 300,
    ):
        self.model = model
        self.host = host
        self.timeout_seconds = timeout_seconds
        self.fact_repository = FactRepository()
        self.entity_repository = EntityRepository()
        self.ontology_repository = OntologyRepository()
        self.relationship_repository = RelationshipRepository()
        self.domain_repository = DomainModelRepository()
        self.actors_repository = ActorsRepository()
        self.process_repository = ProcessRepository()
        self.project_repository = ProjectRepository()

    def build_and_save_summary(self):
        context = self.collect_context()
        summary = self.generate_summary(context)

        summary_id = self.project_repository.save_summary(
            title="Project Summary",
            summary=summary,
            metadata={
                "builder": "project_summary_builder_v3_with_processes",
                "model": self.model,
                "stats": context.get("stats", {}),
            },
        )

        return {"summary_id": summary_id, "summary": summary, "context": context}

    def collect_context(self):
        stats = self.project_repository.get_model_statistics()
        actors = self.actors_repository.list_actors(limit=80)
        processes = self.process_repository.list_processes(limit=80)
        domain_objects = self.domain_repository.list_domain_objects(limit=120)
        ontology = self.ontology_repository.list_entity_ontology(limit=160)
        relationships = self.relationship_repository.list_relationships(limit=150)
        facts = self.fact_repository.list_facts(limit=250)

        high_value_facts = [
            fact for fact in facts
            if fact.get("fact_type") in (
                "business_rule", "requirement", "decision", "risk", "question",
                "integration", "process", "api", "data_model", "workflow",
                "constraint", "dependency",
            )
        ][:180]

        return {
            "stats": stats,
            "actors": actors,
            "processes": processes,
            "domain_objects": domain_objects,
            "ontology": ontology,
            "relationships": relationships,
            "facts": high_value_facts,
        }

    def generate_summary(self, context: dict):
        provider = create_text_provider(
            provider_name="ollama",
            model=self.model,
            host=self.host,
            timeout_seconds=self.timeout_seconds,
        )
        context_text = self._format_context(context)

        prompt = f"""
You are a Senior Business/System Analyst building a stable Project Summary from structured Project Intelligence data.

Return Markdown only.
Use ONLY provided context. Do not invent facts.
Prefer Project Intelligence layers over raw facts:
1. Actors
2. Processes
3. Domain Objects
4. Ontology and Relationships
5. Facts

Cite evidence using [process:ID], [actor:ID], [domain_object:ID], [relationship:ID], [fact:ID] where useful.

Required sections:

# Project Summary

## 1. What the project is about
Explain the product/domain in 3-7 sentences.

## 2. Main actors and responsibilities
Use Actor Profiles.

## 3. Main business processes
Use Process Profiles. Include participants and major steps.

## 4. Main business objects / domain model
Use Domain Objects.

## 5. Integrations, APIs, technical objects
Use ontology, relationships, and facts.

## 6. Important business rules and requirements
List the most important rules/requirements.

## 7. Risks, constraints, and open questions
List risks, constraints, assumptions, missing areas.

## 8. Current confidence and gaps
Explain where the model is strong and where it is weak.

PROJECT INTELLIGENCE CONTEXT:
{context_text}
"""
        return provider.generate(prompt).strip()

    def _format_context(self, context: dict):
        parts = []
        parts.append("## MODEL STATISTICS")
        parts.append(str(context.get("stats", {})))

        actors = context.get("actors", [])
        if actors:
            parts.append("\n## ACTOR PROFILES")
            for actor in actors:
                parts.append(
                    f"- [actor:{actor.get('id')}] {actor.get('name')} "
                    f"type={actor.get('actor_type')} confidence={actor.get('confidence')} "
                    f"description={actor.get('description')} "
                    f"responsibilities={actor.get('responsibilities')[:8]} "
                    f"participates_in={actor.get('participates_in')[:8]}"
                )

        processes = context.get("processes", [])
        if processes:
            parts.append("\n## PROCESS PROFILES")
            for process in processes:
                parts.append(
                    f"- [process:{process.get('id')}] {process.get('name')} "
                    f"type={process.get('process_type')} confidence={process.get('confidence')} "
                    f"goal={process.get('goal')} description={process.get('description')} "
                    f"participants={process.get('participants')[:8]} "
                    f"objects={process.get('business_objects')[:8]} "
                    f"steps={process.get('steps')[:10]} "
                    f"rules={process.get('rules')[:8]}"
                )

        domain_objects = context.get("domain_objects", [])
        if domain_objects:
            parts.append("\n## DOMAIN OBJECTS")
            for item in domain_objects:
                parts.append(
                    f"- [domain_object:{item.get('id')}] {item.get('name')} "
                    f"type={item.get('object_type')} confidence={item.get('confidence')} "
                    f"description={item.get('description')} "
                    f"attributes={item.get('attributes')[:8]} relationships={item.get('relationships')[:8]}"
                )

        ontology = context.get("ontology", [])
        if ontology:
            parts.append("\n## ONTOLOGY")
            for row in ontology[:100]:
                parts.append(
                    f"- [entity:{row.get('entity_id')}] {row.get('entity_name')} "
                    f"ontology={row.get('ontology_type')} confidence={row.get('confidence')} reason={row.get('reason')}"
                )

        relationships = context.get("relationships", [])
        if relationships:
            parts.append("\n## RELATIONSHIPS")
            for rel in relationships[:120]:
                parts.append(
                    f"- [relationship:{rel.get('id')}] {rel.get('from_entity_name')} → "
                    f"{rel.get('predicate')} → {rel.get('to_entity_name')} "
                    f"confidence={rel.get('confidence')} source={rel.get('source')}"
                )

        facts = context.get("facts", [])
        if facts:
            parts.append("\n## HIGH VALUE FACTS")
            for fact in facts[:160]:
                parts.append(
                    f"- [fact:{fact.get('id')}] type={fact.get('fact_type')} "
                    f"{fact.get('subject')} → {fact.get('predicate')} → {fact.get('object')} "
                    f"confidence={fact.get('confidence')} source={fact.get('source')}"
                )

        return "\n".join(parts)

