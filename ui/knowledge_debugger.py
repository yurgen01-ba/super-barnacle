from __future__ import annotations
import streamlit as st
from repositories.knowledge_provenance_repository import knowledge_provenance_repository
ARTIFACT_TYPES=['all','raw_transcript_segment','clean_transcript_segment','rejected_transcript_segment','extracted_items_raw','accepted_facts','rejected_facts','ontology_trace','project_model_snapshot','reasoning_context','final_prompt','final_answer']
def render_knowledge_debugger(project_id='default'):
    st.header('Knowledge Debugger')
    st.caption('Trace source → transcript → facts → ontology → project model → prompt → answer.')
    c1,c2=st.columns(2)
    with c1: artifact_type=st.selectbox('Artifact type', ARTIFACT_TYPES)
    with c2: source_id=st.text_input('Source id filter','')
    records=knowledge_provenance_repository.list_records(project_id=project_id,source_id=source_id.strip() or None,artifact_type=None if artifact_type=='all' else artifact_type,limit=300)
    st.caption(f'Showing {len(records)} provenance record(s).')
    for r in records:
        with st.expander(f"[{r['artifact_type']}] {r['title']}", expanded=False):
            st.write({k:r[k] for k in ['id','source_id','source_type','artifact_type','stage','created_at','metadata']})
            st.text_area('Content', value=r['content'], height=320, key=f"prov_content_{r['id']}")
