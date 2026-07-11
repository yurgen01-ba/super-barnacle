from memory.db import get_connection
from ai.question_intent import classify_question_intent
from repositories.entity_repository import EntityRepository
from repositories.project_repository import ProjectRepository
from repositories.relationship_repository import RelationshipRepository

try:
    from repositories.domain_model_repository import DomainModelRepository
except Exception:
    DomainModelRepository = None

try:
    from repositories.actors_repository import ActorsRepository
except Exception:
    ActorsRepository = None

try:
    from repositories.process_repository import ProcessRepository
except Exception:
    ProcessRepository = None


class ChatContextRepository:
    """
    Model-first context retrieval for AI Analyst.

    Important behavior:
    - Overview questions use Project Summary + model repositories first.
    - Chunks are used only as fallback/support, never as the main context for overview.
    - Missing optional repositories do not break chat during transitional commits.
    """

    HIGH_VALUE_TYPES = [
        "decision", "requirement", "business_rule", "risk", "question", "integration",
        "action_item", "api", "data_model", "process", "constraint", "dependency",
        "bug", "feature",
    ]

    INTENT_FACT_TYPES = {
        "requirements": ["requirement", "business_rule", "constraint", "feature"],
        "risks": ["risk", "constraint", "bug", "dependency"],
        "open_questions": ["question", "assumption", "risk"],
        "integrations": ["integration", "api", "dependency", "technical_object"],
        "processes": ["process", "workflow", "business_rule", "requirement"],
        "actors": ["role", "business_rule", "requirement", "process", "workflow"],
        "decisions": ["decision", "business_rule", "assumption"],
        "entity_deep_dive": ["business_rule", "requirement", "decision", "risk", "api", "process", "data_model"],
        "relationships": ["business_rule", "process", "dependency", "integration"],
        "project_overview": [
            "business_rule", "requirement", "decision", "integration", "process",
            "workflow", "data_model", "risk", "api", "role",
        ],
        "general": HIGH_VALUE_TYPES,
    }

    def __init__(self):
        self.relationship_repository = RelationshipRepository()
        self.project_repository = ProjectRepository()
        self.entity_repository = EntityRepository()
        self.domain_repository = DomainModelRepository() if DomainModelRepository else None
        self.actors_repository = ActorsRepository() if ActorsRepository else None
        self.process_repository = ProcessRepository() if ProcessRepository else None

    def search_context(
        self,
        query: str,
        knowledge_limit: int = 35,
        chunk_limit: int = 12,
        latest_limit: int = 20,
        relationship_limit: int = 50,
        process_limit: int = 20,
        domain_limit: int = 30,
        actor_limit: int = 20,
        include_project_summary: bool = True,
    ):
        query = (query or "").strip()
        intent = classify_question_intent(query)
        terms = self._extract_terms(query)
        intent_name = intent.get("intent")

        project_summary = self.project_repository.get_latest_summary() if include_project_summary else None

        domain_objects = self._retrieve_domain_objects(query, terms, intent, limit=domain_limit)
        actors = self._retrieve_actors(query, terms, intent, limit=actor_limit)
        process_profiles = self._retrieve_process_profiles(query, terms, intent, limit=process_limit)
        entity_profiles = self._retrieve_entity_profiles(intent, terms)
        relationships = self._retrieve_relationships(query, terms, intent, limit=relationship_limit)
        facts = self._retrieve_facts_by_intent(intent, terms, limit=80)

        knowledge_items = self._rank_knowledge(terms, intent=intent, limit=knowledge_limit)
        latest_high_value = self.get_latest_high_value_knowledge(limit=latest_limit)
        merged_knowledge = self._merge_by_id(knowledge_items + latest_high_value, limit=knowledge_limit + latest_limit)

        # Critical fix: overview answers should not be driven by arbitrary source chunks.
        # Chunks are only allowed when the structured Project Model is almost empty.
        structured_count = sum([
            1 if project_summary else 0,
            len(domain_objects), len(actors), len(process_profiles), len(entity_profiles), len(relationships), len(facts),
        ])

        chunks = []
        if intent_name not in ("project_overview", "relationships", "processes", "actors"):
            chunks = self._rank_chunks(terms, limit=chunk_limit)
            if not chunks:
                chunks = self.get_latest_chunks(limit=min(chunk_limit, 8))
        elif structured_count <= 3:
            chunks = self._rank_chunks(terms, limit=min(chunk_limit, 5))

        return {
            "intent": intent,
            "project_summary": project_summary,
            "domain_objects": domain_objects,
            "actors": actors,
            "process_profiles": process_profiles,
            "entity_profiles": entity_profiles,
            "relationships": relationships,
            "facts": facts,
            "knowledge_items": merged_knowledge,
            "chunks": chunks,
            "project_memory_summary": self.get_memory_type_counts(),
            "retrieval_terms": terms,
            "retrieval_debug": {
                "structured_count": structured_count,
                "chunks_allowed": bool(chunks),
                "strategy": self._strategy_name(intent_name, structured_count),
            },
        }

    def _strategy_name(self, intent_name: str, structured_count: int):
        if intent_name == "project_overview":
            return "model_first_overview" if structured_count > 3 else "overview_with_chunk_fallback"
        if intent_name in ("processes", "actors", "relationships"):
            return f"model_first_{intent_name}"
        return "hybrid_model_memory"

    def _retrieve_domain_objects(self, query: str, terms, intent: dict, limit: int):
        if not self.domain_repository:
            return []

        intent_name = intent.get("intent")
        rows = []

        if intent_name == "project_overview":
            return self.domain_repository.list_domain_objects(limit=limit)

        if intent_name in ("entity_deep_dive", "processes", "relationships", "requirements", "risks", "general"):
            if query:
                rows.extend(self.domain_repository.search_domain_objects(query, limit=limit))
            for term in terms[:6]:
                rows.extend(self.domain_repository.search_domain_objects(term, limit=max(5, limit // 2)))

        return self._dedupe_by_id(rows, limit=limit)

    def _retrieve_actors(self, query: str, terms, intent: dict, limit: int):
        if not self.actors_repository:
            return []

        intent_name = intent.get("intent")
        rows = []

        if intent_name in ("project_overview", "actors"):
            return self.actors_repository.list_actors(limit=limit)

        if intent_name in ("processes", "entity_deep_dive", "relationships", "general"):
            if query:
                rows.extend(self.actors_repository.search_actors(query, limit=limit))
            for term in terms[:6]:
                rows.extend(self.actors_repository.search_actors(term, limit=max(5, limit // 2)))

        return self._dedupe_by_id(rows, limit=limit)

    def _retrieve_process_profiles(self, query: str, terms, intent: dict, limit: int):
        if not self.process_repository:
            return []

        rows = []
        intent_name = intent.get("intent")

        if intent_name in ("project_overview", "processes"):
            if query:
                rows.extend(self.process_repository.search_processes(query, limit=limit))
            for term in terms[:6]:
                rows.extend(self.process_repository.search_processes(term, limit=max(5, limit // 2)))
            if intent_name == "project_overview":
                rows.extend(self.process_repository.list_processes(limit=limit))
        elif intent_name in ("entity_deep_dive", "relationships", "general"):
            if query:
                rows.extend(self.process_repository.search_processes(query, limit=limit))
            for term in terms[:6]:
                rows.extend(self.process_repository.search_processes(term, limit=max(5, limit // 2)))

        return self._dedupe_by_id(rows, limit=limit)

    def _retrieve_entity_profiles(self, intent: dict, terms):
        entity_names = list(intent.get("entities") or [])
        if not entity_names and intent.get("intent") in ("entity_deep_dive", "relationships", "processes"):
            for term in terms[:5]:
                matches = self.entity_repository.search_entities(term, limit=3)
                for match in matches:
                    if match.get("name") not in entity_names:
                        entity_names.append(match.get("name"))

        profiles = []
        for name in entity_names[:8]:
            entity = self.entity_repository.get_entity_by_name(name)
            if not entity:
                continue
            profile = self.entity_repository.build_entity_profile(entity["id"])
            if profile:
                profiles.append(profile)
        return profiles

    def _retrieve_relationships(self, query: str, terms, intent: dict, limit: int):
        relationships = []
        intent_name = intent.get("intent")

        if intent_name in ("project_overview", "relationships", "entity_deep_dive", "processes", "integrations", "actors"):
            if query:
                relationships.extend(self.relationship_repository.search_relationships(query, limit=limit))
            for entity_name in intent.get("entities", []):
                relationships.extend(self.relationship_repository.get_entity_neighborhood(entity_name, limit=limit))
            for term in terms[:6]:
                relationships.extend(self.relationship_repository.get_entity_neighborhood(term, limit=max(5, limit // 2)))

            if intent_name == "project_overview" and not relationships:
                relationships.extend(self.relationship_repository.list_relationships(limit=min(limit, 50)))
        elif query:
            relationships.extend(self.relationship_repository.search_relationships(query, limit=limit // 2))

        return self._dedupe_by_id(relationships, limit=limit)

    def _retrieve_facts_by_intent(self, intent: dict, terms, limit: int):
        fact_types = self.INTENT_FACT_TYPES.get(intent.get("intent"), self.HIGH_VALUE_TYPES)
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ",".join("?" for _ in fact_types)
        cur.execute(
            f"""
            SELECT *
            FROM facts
            WHERE fact_type IN ({placeholders})
            ORDER BY confidence DESC, updated_at DESC
            LIMIT 1000
            """,
            fact_types,
        )
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()

        if intent.get("intent") == "project_overview":
            return rows[:limit]

        scored = []
        for row in rows:
            text = " ".join([
                str(row.get("subject") or ""), str(row.get("predicate") or ""),
                str(row.get("object") or ""), str(row.get("source") or ""),
                str(row.get("fact_type") or ""),
            ]).lower()
            score = 0
            for term in terms:
                if term in text:
                    score += 3
            for entity in intent.get("entities", []):
                if entity.lower() in text:
                    score += 6
            if score > 0:
                row["_score"] = score
                scored.append(row)
        scored.sort(key=lambda item: item.get("_score", 0), reverse=True)
        return scored[:limit] if scored else rows[:min(limit, 25)]

    def _rank_knowledge(self, terms, intent: dict, limit: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, type, title, content, source, created_at
            FROM knowledge
            ORDER BY created_at DESC
            LIMIT 1000
            """
        )
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()

        scored = []
        preferred_types = self.INTENT_FACT_TYPES.get(intent.get("intent"), self.HIGH_VALUE_TYPES)
        for row in rows:
            text = " ".join([
                str(row.get("type") or ""), str(row.get("title") or ""),
                str(row.get("content") or ""), str(row.get("source") or ""),
            ]).lower()
            score = 0
            for term in terms:
                if term in text:
                    score += 3
                if term in str(row.get("title") or "").lower():
                    score += 4
                if term in str(row.get("type") or "").lower():
                    score += 2
            if row.get("type") in preferred_types:
                score += 3
            for entity in intent.get("entities", []):
                if entity.lower() in text:
                    score += 6
            if score > 0:
                row["_score"] = score
                scored.append(row)
        scored.sort(key=lambda item: item.get("_score", 0), reverse=True)
        return scored[:limit]

    def _rank_chunks(self, terms, limit: int):
        if not terms:
            return []
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.content, c.content_length, c.created_at,
                   d.name AS document_name, d.source_type AS source_type
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.created_at DESC
            LIMIT 500
            """
        )
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()

        scored = []
        for row in rows:
            text = " ".join([
                str(row.get("document_name") or ""), str(row.get("source_type") or ""), str(row.get("content") or ""),
            ]).lower()
            score = 0
            for term in terms:
                if term in text:
                    score += 2
            if score > 0:
                row["_score"] = score
                scored.append(row)
        scored.sort(key=lambda item: item.get("_score", 0), reverse=True)
        return scored[:limit]

    def get_latest_high_value_knowledge(self, limit: int = 20):
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ",".join("?" for _ in self.HIGH_VALUE_TYPES)
        cur.execute(
            f"""
            SELECT id, type, title, content, source, created_at
            FROM knowledge
            WHERE type IN ({placeholders})
            ORDER BY created_at DESC
            LIMIT ?
            """,
            self.HIGH_VALUE_TYPES + [limit],
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_latest_chunks(self, limit: int = 8):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.content, c.content_length, c.created_at,
                   d.name AS document_name, d.source_type AS source_type
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_memory_type_counts(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT type, COUNT(*) AS count
            FROM knowledge
            GROUP BY type
            ORDER BY count DESC
            """
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def _extract_terms(self, query: str):
        stop_words = {
            "что", "как", "где", "когда", "почему", "какие", "какой", "какая", "какое",
            "the", "and", "for", "with", "from", "about", "это", "или",
            "есть", "надо", "нужно", "please", "tell", "show", "list",
            "опиши", "кратко", "суть", "проекта", "проект", "вкратце", "коротко", "о", "чем",
        }
        raw_terms = [term.strip(".,:;!?()[]{}\"'").lower() for term in query.split()]
        return [term for term in raw_terms if len(term) >= 3 and term not in stop_words][:12]

    def _dedupe_by_id(self, items, limit: int):
        seen = set()
        result = []
        for item in items:
            item_id = item.get("id")
            # Some repositories may return rows from different tables with same id. Prefix by class-like keys when possible.
            key = (item.get("name"), item_id) if item.get("name") else item_id
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
            if len(result) >= limit:
                break
        return result

    def _merge_by_id(self, items, limit: int):
        seen = set()
        result = []
        for item in items:
            item_id = item.get("id")
            if item_id in seen:
                continue
            seen.add(item_id)
            result.append(item)
            if len(result) >= limit:
                break
        return result

