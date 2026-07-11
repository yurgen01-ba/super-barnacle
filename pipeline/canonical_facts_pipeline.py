from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ai.fact_quality import filter_quality_facts
from graph.fact_graph_builder import FactGraphBuilder
from graph.graph_diagnostics import graph_diagnostics
from graph.project_graph_writer import ProjectGraphWriter
from quality.confidence_gate import confidence_gate
from repositories.source_document_repository import source_document_repository
from summary.incremental_summary_engine import incremental_summary_engine

@dataclass(slots=True)
class CanonicalFact:
    subject: str; predicate: str; object: str; source_document_id: str = ""; source_chunk_id: str = ""; confidence: float = 0.7; metadata: dict[str, Any] = field(default_factory=dict)
    @property
    def title(self): return f"{self.subject} {self.predicate} {self.object}"
    @property
    def description(self): return self.title
    def to_node_dict(self): return {"type":"fact","title":self.title,"description":self.description,"content":self.description,"confidence":self.confidence,"source_document_id":self.source_document_id,"source_chunk_id":self.source_chunk_id,**self.metadata}

class CanonicalFactsPipeline:
    def __init__(self, graph_writer=None, fact_graph_builder=None): self.graph_writer=graph_writer or ProjectGraphWriter(); self.fact_graph_builder=fact_graph_builder or FactGraphBuilder()
    def process_extracted_items(self, source_type: str, title: str, original_text: str, extracted_items: list[dict], project_id: str = "default", source_ref: str = "") -> dict:
        quality_items=filter_quality_facts(extracted_items or []); accepted_items=confidence_gate.filter(quality_items)
        graph_diagnostics.record(stage="canonical_pipeline:start", message=f"Processing extracted items from {source_type}: {title}", project_id=project_id, counts={"extracted_items":len(extracted_items or []),"quality_items":len(quality_items),"accepted_items":len(accepted_items),"dropped_by_confidence_gate":len(quality_items)-len(accepted_items)}, metadata={"source_type":source_type,"source_ref":source_ref})
        doc=source_document_repository.save_document(source_type=source_type,title=title,original_text=original_text,project_id=project_id,source_ref=source_ref)
        facts=self._items_to_facts(accepted_items, source_document_id=doc.id); fact_items=[f.to_node_dict() for f in facts]
        graph_result=self.graph_writer.save_items(fact_items, default_type="fact", source=f"canonical_facts_pipeline:{source_type}")
        model_build_result=self.fact_graph_builder.build_from_items(fact_items, project_id=project_id, source=f"fact_graph_builder:{source_type}")
        project_model=incremental_summary_engine.update_from_facts(accepted_items, project_id=project_id)
        graph_diagnostics.record(stage="canonical_pipeline:project_model_updated", message="Project Model updated incrementally from accepted facts", project_id=project_id, counts={"project_model_version":project_model.version,"actors":len(project_model.actors),"processes":len(project_model.processes),"entities":len(project_model.entities),"business_rules":len(project_model.business_rules),"integrations":len(project_model.integrations)})
        return {"source_document":doc,"facts":facts,"graph_result":graph_result,"model_build_result":model_build_result,"quality_items":quality_items,"accepted_items":accepted_items,"project_model":project_model.to_dict()}
    def _items_to_facts(self, items, source_document_id):
        facts=[]
        for item in items:
            if not isinstance(item, dict): continue
            subject=str(item.get("subject") or item.get("title") or item.get("type") or "Project"); predicate=str(item.get("predicate") or "has"); obj=str(item.get("object") or item.get("content") or item.get("description") or item.get("text") or "")
            if obj.strip(): facts.append(CanonicalFact(subject=subject,predicate=predicate,object=obj,source_document_id=source_document_id,confidence=float(item.get("confidence") or 0.7),metadata={"original_item":item}))
        return facts
