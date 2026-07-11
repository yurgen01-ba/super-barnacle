import streamlit as st

from repositories.fact_repository import FactRepository


def render_facts_tab():
    st.header("Canonical Facts")
    st.caption(
        "Canonical Facts are the new foundation layer: subject → predicate → object."
    )

    fact_repository = FactRepository()

    counts = fact_repository.get_fact_counts()

    if counts:
        st.subheader("Fact counts by type")
        st.dataframe(counts, width="stretch")
    else:
        st.info("No canonical facts stored yet.")

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        query = st.text_input(
            "Search facts",
            placeholder="Merchant, Advance, Funding, Underwriting...",
            key="facts_search_query",
        )

    with col2:
        limit = st.slider("Limit", 20, 500, 100, 20, key="facts_limit")

    facts = fact_repository.search_facts(query, limit=limit)

    st.subheader(f"Facts ({len(facts)})")

    if not facts:
        st.warning("No facts found.")
        return

    for fact in facts:
        with st.expander(
            f"#{fact['id']} | {fact['subject']} → {fact['predicate']} → {fact['object'][:80]}",
            expanded=False,
        ):
            st.write(
                {
                    "id": fact["id"],
                    "subject": fact["subject"],
                    "predicate": fact["predicate"],
                    "object": fact["object"],
                    "fact_type": fact["fact_type"],
                    "confidence": fact["confidence"],
                    "status": fact["status"],
                    "source": fact["source"],
                    "evidence": fact["evidence"],
                    "version": fact["version"],
                    "created_at": fact["created_at"],
                    "updated_at": fact["updated_at"],
                }
            )

