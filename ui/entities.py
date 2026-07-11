import streamlit as st

from builders.entity_builder import EntityBuilder
from repositories.entity_repository import EntityRepository


def render_entities_tab():
    st.header("Entities")
    st.caption(
        "Entities are built from Canonical Facts and represent project objects, roles, processes, products, integrations, APIs, and UI elements."
    )

    entity_repository = EntityRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Build / Refresh Entities from Facts", key="build_entities_from_facts"):
            with st.spinner("Building entities from Canonical Facts..."):
                result = EntityBuilder().build_entities_from_facts()

            st.success(
                f"Processed {result['facts_processed']} facts. "
                f"Entities total: {result['entities_total']}. "
                f"Links created: {result['links_created']}."
            )

            with st.expander("Build result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 29 creates the first Entity layer. Later commits will add richer entity summaries, relationships graph, and entity-based chat retrieval."
        )

    query = st.text_input(
        "Search entities",
        placeholder="Merchant, Advance, Funding, Underwriting...",
        key="entities_search_query",
    )

    limit = st.slider("Entities limit", 20, 500, 100, 20, key="entities_limit")

    entities = entity_repository.search_entities(query, limit=limit)

    st.subheader(f"Entities ({len(entities)})")

    if not entities:
        st.warning("No entities yet. Build entities after Canonical Facts are extracted.")
        return

    for entity in entities:
        label = (
            f"#{entity['id']} | {entity['name']} "
            f"({entity.get('entity_type') or 'unknown'}) — "
            f"{entity.get('facts_count', 0)} facts"
        )

        with st.expander(label, expanded=False):
            profile = entity_repository.build_entity_profile(entity["id"])

            if not profile:
                st.warning("Entity profile not found.")
                continue

            st.write(
                {
                    "id": entity["id"],
                    "name": entity["name"],
                    "entity_type": entity.get("entity_type"),
                    "description": entity.get("description"),
                    "confidence": entity.get("confidence"),
                    "facts_count": profile.get("facts_count"),
                    "created_at": entity.get("created_at"),
                    "updated_at": entity.get("updated_at"),
                }
            )

            grouped = profile.get("grouped_facts", {})

            if grouped:
                st.markdown("#### Facts by type")

                for fact_type, facts in grouped.items():
                    with st.expander(f"{fact_type} ({len(facts)})", expanded=False):
                        for fact in facts[:50]:
                            st.markdown(
                                f"- `[fact:{fact['id']}]` **{fact['subject']}** → "
                                f"`{fact['predicate']}` → **{fact['object']}** "
                                f"_(confidence: {fact['confidence']}, source: {fact.get('source')})_"
                            )

            outgoing = profile.get("outgoing_relationships", [])
            incoming = profile.get("incoming_relationships", [])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Outgoing")
                if outgoing:
                    for fact in outgoing[:30]:
                        st.markdown(
                            f"- {fact['subject']} → `{fact['predicate']}` → {fact['object']}"
                        )
                else:
                    st.caption("No outgoing relationships yet.")

            with col2:
                st.markdown("#### Incoming")
                if incoming:
                    for fact in incoming[:30]:
                        st.markdown(
                            f"- {fact['subject']} → `{fact['predicate']}` → {fact['object']}"
                        )
                else:
                    st.caption("No incoming relationships yet.")

