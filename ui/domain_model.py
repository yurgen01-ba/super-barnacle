import streamlit as st

from builders.domain_model_builder import DomainModelBuilder
from repositories.domain_model_repository import DomainModelRepository


def render_domain_model_tab():
    st.header("Domain Model")
    st.caption(
        "Domain Model turns ontology-classified entities into DDD-style business objects with attributes, relationships, rules, lifecycle, and evidence."
    )

    repository = DomainModelRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Build / Refresh Domain Model", key="build_domain_model"):
            with st.spinner("Building Domain Model from Ontology, Entities, Facts, and Relationships..."):
                result = DomainModelBuilder().build_domain_model()

            st.success(
                f"Built {result['domain_objects_built']} domain objects from "
                f"{result['domain_candidates']} candidates."
            )

            with st.expander("Build result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 35 builds the first DDD-like layer. Next builders can use it for Actors, Processes, Modules, Integrations, and Overview 2.0."
        )

    stats = repository.get_domain_model_statistics()

    with st.expander("Domain Model statistics", expanded=True):
        st.write(stats)

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        query = st.text_input(
            "Search domain objects",
            placeholder="Merchant, Advance, Funding, Worksheet...",
            key="domain_model_search_query",
        )

    with col2:
        limit = st.slider("Limit", 20, 500, 100, 20, key="domain_model_limit")

    domain_objects = repository.search_domain_objects(query, limit=limit)

    st.subheader(f"Domain objects ({len(domain_objects)})")

    if not domain_objects:
        st.warning("No domain objects yet. Build the Domain Model after Ontology and Relationships are available.")
        return

    for item in domain_objects:
        label = (
            f"#{item['id']} | {item['name']} → {item.get('object_type')} "
            f"(confidence: {item.get('confidence')})"
        )

        with st.expander(label, expanded=False):
            st.markdown(f"### {item['name']}")
            st.write(
                {
                    "id": item["id"],
                    "entity_id": item["entity_id"],
                    "object_type": item.get("object_type"),
                    "ontology_type": item.get("ontology_type"),
                    "confidence": item.get("confidence"),
                    "description": item.get("description"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                }
            )

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("#### Attributes / states")
                attrs = item.get("attributes", [])
                if attrs:
                    for attr in attrs[:50]:
                        st.markdown(
                            f"- **{attr.get('name')}** via `{attr.get('predicate')}` "
                            f"[fact:{attr.get('fact_id')}]"
                        )
                else:
                    st.caption("No attributes yet.")

                st.markdown("#### Lifecycle")
                lifecycle = item.get("lifecycle", [])
                if lifecycle:
                    for step in lifecycle[:50]:
                        ref = f"[fact:{step.get('fact_id')}]" if step.get("fact_id") else f"[relationship:{step.get('relationship_id')}]"
                        st.markdown(
                            f"- **{step.get('step_or_state')}** via `{step.get('predicate')}` {ref}"
                        )
                else:
                    st.caption("No lifecycle hints yet.")

            with col_b:
                st.markdown("#### Relationships")
                rels = item.get("relationships", [])
                if rels:
                    for rel in rels[:50]:
                        st.markdown(
                            f"- `{rel.get('direction')}` **{rel.get('predicate')}** → "
                            f"{rel.get('related_object')} [relationship:{rel.get('relationship_id')}]"
                        )
                else:
                    st.caption("No relationships yet.")

                st.markdown("#### Rules / requirements / risks")
                rules = item.get("rules", [])
                if rules:
                    for rule in rules[:50]:
                        st.markdown(
                            f"- `{rule.get('type')}` {rule.get('statement')} [fact:{rule.get('fact_id')}]"
                        )
                else:
                    st.caption("No rules yet.")

            with st.expander("Evidence", expanded=False):
                st.write(item.get("evidence", []))

