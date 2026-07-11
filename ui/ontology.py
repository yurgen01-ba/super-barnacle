import streamlit as st

from builders.ontology_builder import OntologyBuilder
from core.ontology import ONTOLOGY_TYPE_DESCRIPTIONS, ONTOLOGY_TYPES
from repositories.ontology_repository import OntologyRepository


def render_ontology_tab():
    st.header("Ontology")
    st.caption(
        "Ontology classifies Entities into stable Project Model types: actors, processes, modules, integrations, business objects, APIs, screens, etc."
    )

    ontology_repository = OntologyRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Classify / Refresh Entity Ontology", key="classify_entity_ontology"):
            with st.spinner("Classifying entities into ontology types..."):
                result = OntologyBuilder().classify_entities()

            st.success(
                f"Processed {result['entities_processed']} entities. "
                f"Classified: {result['classified']}. Unknown: {result['unknown']}."
            )

            with st.expander("Classification result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 34 uses deterministic heuristics first. Later commits can add AI-assisted classification for low-confidence or unknown entities."
        )

    counts = ontology_repository.get_ontology_counts()

    if counts:
        st.subheader("Ontology counts")
        st.dataframe(counts, width="stretch")
    else:
        st.info("No ontology classifications yet.")

    with st.expander("Ontology type dictionary", expanded=False):
        for ontology_type in ONTOLOGY_TYPES:
            st.markdown(
                f"- **{ontology_type}** — {ONTOLOGY_TYPE_DESCRIPTIONS.get(ontology_type, '')}"
            )

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        query = st.text_input(
            "Search ontology",
            placeholder="Merchant, actor, process, integration...",
            key="ontology_search_query",
        )

    with col2:
        limit = st.slider("Limit", 20, 1000, 200, 20, key="ontology_limit")

    rows = ontology_repository.search_entity_ontology(query, limit=limit)

    st.subheader(f"Classified entities ({len(rows)})")

    if not rows:
        st.warning("No classified entities yet.")
        return

    for row in rows:
        label = (
            f"#{row['entity_id']} | {row['entity_name']} → "
            f"{row['ontology_type']} "
            f"(confidence: {row['confidence']})"
        )

        with st.expander(label, expanded=False):
            st.write(
                {
                    "entity_id": row["entity_id"],
                    "entity_name": row["entity_name"],
                    "entity_type": row.get("entity_type"),
                    "ontology_type": row["ontology_type"],
                    "confidence": row["confidence"],
                    "classification_method": row.get("classification_method"),
                    "reason": row.get("reason"),
                    "description": row.get("entity_description"),
                    "metadata_json": row.get("metadata_json"),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                }
            )

