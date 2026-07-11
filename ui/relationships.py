import streamlit as st

from builders.relationship_builder import RelationshipBuilder
from repositories.relationship_repository import RelationshipRepository


def render_relationships_tab():
    st.header("Relationships")
    st.caption(
        "Relationships connect Entities through Canonical Facts: Entity A → predicate → Entity B."
    )

    relationship_repository = RelationshipRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Build / Refresh Relationships from Facts", key="build_relationships_from_facts"):
            with st.spinner("Building relationships from Canonical Facts..."):
                result = RelationshipBuilder().build_relationships_from_facts()

            st.success(
                f"Processed {result['facts_processed']} facts. "
                f"Relationships total: {result['relationships_total']}. "
                f"Created/updated: {result['created_or_updated']}."
            )

            with st.expander("Build result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 31 adds the first graph layer. Later chat retrieval can use these relationships to answer graph-style questions."
        )

    counts = relationship_repository.get_relationship_counts()

    if counts:
        with st.expander("Relationship counts by predicate", expanded=False):
            st.dataframe(counts, width="stretch")

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        query = st.text_input(
            "Search relationships",
            placeholder="Merchant, Advance, Funding, approved_by...",
            key="relationships_search_query",
        )

    with col2:
        limit = st.slider("Limit", 20, 1000, 200, 20, key="relationships_limit")

    relationships = relationship_repository.search_relationships(query, limit=limit)

    st.subheader(f"Relationships ({len(relationships)})")

    if not relationships:
        st.warning("No relationships yet. Build relationships after Entities and Canonical Facts are available.")
        return

    for rel in relationships:
        label = (
            f"#{rel['id']} | {rel['from_entity_name']} "
            f"→ {rel['predicate']} → {rel['to_entity_name']}"
        )

        with st.expander(label, expanded=False):
            st.write(
                {
                    "id": rel["id"],
                    "from_entity": rel["from_entity_name"],
                    "from_entity_type": rel.get("from_entity_type"),
                    "predicate": rel["predicate"],
                    "to_entity": rel["to_entity_name"],
                    "to_entity_type": rel.get("to_entity_type"),
                    "confidence": rel.get("confidence"),
                    "source": rel.get("source"),
                    "evidence": rel.get("evidence"),
                    "fact_id": rel.get("fact_id"),
                    "created_at": rel.get("created_at"),
                    "updated_at": rel.get("updated_at"),
                }
            )

            if rel.get("fact_id"):
                st.markdown(
                    f"Evidence fact: `[fact:{rel['fact_id']}]` "
                    f"{rel.get('fact_subject')} → `{rel.get('fact_predicate')}` → {rel.get('fact_object')}"
                )

    st.divider()
    st.subheader("Entity neighborhood")

    entity_name = st.text_input(
        "Entity name",
        placeholder="Merchant",
        key="relationship_neighborhood_entity",
    )

    if entity_name:
        neighborhood = relationship_repository.get_entity_neighborhood(entity_name, limit=200)

        if not neighborhood:
            st.warning("No relationships found for this entity.")
        else:
            st.markdown(f"#### Relationships around `{entity_name}`")
            for rel in neighborhood:
                st.markdown(
                    f"- `{rel['from_entity_name']}` → **{rel['predicate']}** → `{rel['to_entity_name']}` "
                    f"_confidence: {rel.get('confidence')}_"
                )

