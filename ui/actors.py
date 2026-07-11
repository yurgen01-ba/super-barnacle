import streamlit as st

from builders.actors_builder import ActorsBuilder
from repositories.actors_repository import ActorsRepository


def render_actors_tab():
    st.header("Actors")
    st.caption(
        "Actors represent people, roles, organizations, and system users with responsibilities, owned objects, interactions, permissions, and evidence."
    )

    repository = ActorsRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Build / Refresh Actors", key="build_actors"):
            with st.spinner("Building Actor Profiles from Ontology, Domain Model, Facts, and Relationships..."):
                result = ActorsBuilder().build_actors()

            st.success(
                f"Built {result['actors_built']} actors from "
                f"{result['actor_candidates']} candidates."
            )

            with st.expander("Build result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 36 adds the first Project Intelligence layer. Actor Profiles will be used by Processes, Overview 2.0, and Chat."
        )

    with st.expander("Actor statistics", expanded=True):
        st.write(repository.get_actor_statistics())

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        query = st.text_input("Search actors", placeholder="Merchant, Underwriter, Funder, ISO...", key="actors_search_query")

    with col2:
        limit = st.slider("Limit", 20, 500, 100, 20, key="actors_limit")

    actors = repository.search_actors(query, limit=limit)

    st.subheader(f"Actors ({len(actors)})")

    if not actors:
        st.warning("No actors yet. Build Actors after Ontology and Domain Model are available.")
        return

    for actor in actors:
        label = f"#{actor['id']} | {actor['name']} → {actor.get('actor_type')} (confidence: {actor.get('confidence')})"

        with st.expander(label, expanded=False):
            st.markdown(f"### {actor['name']}")
            st.write({
                "id": actor["id"],
                "entity_id": actor["entity_id"],
                "actor_type": actor.get("actor_type"),
                "ontology_type": actor.get("ontology_type"),
                "confidence": actor.get("confidence"),
                "description": actor.get("description"),
                "created_at": actor.get("created_at"),
                "updated_at": actor.get("updated_at"),
            })

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("#### Responsibilities")
                responsibilities = actor.get("responsibilities", [])
                if responsibilities:
                    for item in responsibilities[:50]:
                        ref = f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else f"[relationship:{item.get('relationship_id')}]"
                        st.markdown(f"- {item.get('statement') or item.get('target')} {ref}")
                else:
                    st.caption("No responsibilities yet.")

                st.markdown("#### Participates in")
                participates_in = actor.get("participates_in", [])
                if participates_in:
                    for item in participates_in[:50]:
                        ref = f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else f"[relationship:{item.get('relationship_id')}]"
                        st.markdown(f"- **{item.get('process_or_activity')}** via `{item.get('predicate')}` {ref}")
                else:
                    st.caption("No process participation yet.")

            with col_b:
                st.markdown("#### Owned / related objects")
                owned = actor.get("owned_objects", [])
                if owned:
                    for item in owned[:50]:
                        st.markdown(f"- **{item.get('object')}** via `{item.get('predicate')}` [relationship:{item.get('relationship_id')}]")
                else:
                    st.caption("No owned/related objects yet.")

                st.markdown("#### Interactions")
                interactions = actor.get("interactions", [])
                if interactions:
                    for item in interactions[:50]:
                        st.markdown(f"- `{item.get('direction')}` **{item.get('predicate')}** with {item.get('with')} [relationship:{item.get('relationship_id')}]")
                else:
                    st.caption("No interactions yet.")

            with st.expander("Permissions", expanded=False):
                permissions = actor.get("permissions", [])
                if permissions:
                    for item in permissions[:50]:
                        ref = f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else f"[relationship:{item.get('relationship_id')}]"
                        st.markdown(f"- {item.get('statement')} {ref}")
                else:
                    st.caption("No permissions yet.")

            with st.expander("Evidence", expanded=False):
                st.write(actor.get("evidence", []))

