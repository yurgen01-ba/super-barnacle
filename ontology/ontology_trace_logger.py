from repositories.knowledge_provenance_repository import knowledge_provenance_repository
def log_ontology_trace(fact, resolved_items, project_id='default', source_id=''):
    payload=[{'canonical':getattr(x,'canonical',None),'node_type':getattr(x,'node_type',None),'confidence':getattr(x,'confidence',None),'ru_label':getattr(x,'ru_label',None),'source_text':getattr(x,'source_text','')} for x in (resolved_items or [])]
    title=f"Ontology trace — {str(fact.get('subject') or fact.get('title') or 'fact')[:80]}"
    knowledge_provenance_repository.create(source_id or str(fact.get('source') or 'unknown'),'ontology_resolution','ontology_trace',title,str(payload),'ontology:resolved',project_id,{'resolved_count':len(payload),'fact':fact})
