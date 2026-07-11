from repositories.knowledge_provenance_repository import knowledge_provenance_repository
def log_fact_provenance(source_id, source_type, title, extracted_items, accepted_items, rejected_items, project_id='default'):
    knowledge_provenance_repository.create(source_id,source_type,'extracted_items_raw',f'Raw extracted items — {title}',str(extracted_items or []),'facts:extracted_raw',project_id,{'items_count':len(extracted_items or [])})
    knowledge_provenance_repository.create(source_id,source_type,'accepted_facts',f'Accepted facts — {title}',str(accepted_items or []),'facts:accepted',project_id,{'accepted_count':len(accepted_items or [])})
    knowledge_provenance_repository.create(source_id,source_type,'rejected_facts',f'Rejected facts — {title}',str(rejected_items or []),'facts:rejected',project_id,{'rejected_count':len(rejected_items or []),'reason':'confidence_gate_or_unknown_ontology'})
