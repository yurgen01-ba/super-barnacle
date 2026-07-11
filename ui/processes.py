import streamlit as st

from builders.process_builder import ProcessBuilder
from repositories.process_repository import ProcessRepository


def render_processes_tab():
    st.header("Processes")
    st.caption(
        "Processes describe business workflows with participants, business objects, steps, inputs, outputs, rules, exceptions, and evidence."
    )

    repository = ProcessRepository()

    col_build, col_info = st.columns([0.35, 0.65])

    with col_build:
        if st.button("Build / Refresh Processes", key="build_processes"):
            with st.spinner("Building Process Model from Domain Model, Actors, Facts, and Relationships..."):
                result = ProcessBuilder().build_processes()
            st.success(
                f"Built {result['processes_built']} processes from {result['process_candidates']} candidates."
            )
            with st.expander("Build result", expanded=False):
                st.write(result)

    with col_info:
        st.info(
            "Commit 37 adds Business Process Intelligence. Process Profiles will be used by Project Summary, Chat, and future Impact Analysis."
        )

    with st.expander("Process statistics", expanded=True):
        st.write(repository.get_process_statistics())

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        query = st.text_input(
            "Search processes",
            placeholder="Funding, Underwriting, Application, Repayment...",
            key="processes_search_query",
        )
    with col2:
        limit = st.slider("Limit", 20, 500, 100, 20, key="processes_limit")

    processes = repository.search_processes(query, limit=limit)
    st.subheader(f"Processes ({len(processes)})")

    if not processes:
        st.warning("No processes yet. Build Processes after Domain Model and Actors are available.")
        return

    for process in processes:
        label = f"#{process['id']} | {process['name']} → {process.get('process_type')} (confidence: {process.get('confidence')})"
        with st.expander(label, expanded=False):
            st.markdown(f"### {process['name']}")
            st.write(
                {
                    "id": process["id"],
                    "process_type": process.get("process_type"),
                    "goal": process.get("goal"),
                    "confidence": process.get("confidence"),
                    "description": process.get("description"),
                    "created_at": process.get("created_at"),
                    "updated_at": process.get("updated_at"),
                }
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Participants")
                participants = process.get("participants", [])
                if participants:
                    for item in participants[:50]:
                        ref = f"[relationship:{item.get('relationship_id')}]" if item.get("relationship_id") else f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else ""
                        st.markdown(f"- **{item.get('actor')}** via `{item.get('role') or item.get('source')}` {ref}")
                else:
                    st.caption("No participants yet.")

                st.markdown("#### Steps")
                steps = process.get("steps", [])
                if steps:
                    for item in steps[:80]:
                        ref = f"[relationship:{item.get('relationship_id')}]" if item.get("relationship_id") else f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else ""
                        st.markdown(f"{item.get('order')}. {item.get('step')} {ref}")
                else:
                    st.caption("No steps yet.")

            with col_b:
                st.markdown("#### Business objects")
                objects = process.get("business_objects", [])
                if objects:
                    for item in objects[:50]:
                        ref = f"[relationship:{item.get('relationship_id')}]" if item.get("relationship_id") else f"[fact:{item.get('fact_id')}]" if item.get("fact_id") else ""
                        st.markdown(f"- **{item.get('object')}** via `{item.get('predicate') or item.get('source')}` {ref}")
                else:
                    st.caption("No business objects yet.")

                st.markdown("#### Inputs / Outputs")
                inputs = process.get("inputs", [])
                outputs = process.get("outputs", [])
                if inputs:
                    st.markdown("**Inputs**")
                    for item in inputs[:30]:
                        st.markdown(f"- {item.get('name')} via `{item.get('predicate')}`")
                if outputs:
                    st.markdown("**Outputs**")
                    for item in outputs[:30]:
                        st.markdown(f"- {item.get('name')} via `{item.get('predicate')}`")
                if not inputs and not outputs:
                    st.caption("No inputs/outputs yet.")

            with st.expander("Rules / requirements", expanded=False):
                rules = process.get("rules", [])
                if rules:
                    for item in rules[:80]:
                        st.markdown(f"- `{item.get('type')}` {item.get('statement')} [fact:{item.get('fact_id')}]")
                else:
                    st.caption("No rules yet.")

            with st.expander("Exceptions / risks / open questions", expanded=False):
                exceptions = process.get("exceptions", [])
                if exceptions:
                    for item in exceptions[:80]:
                        st.markdown(f"- `{item.get('type')}` {item.get('statement')} [fact:{item.get('fact_id')}]")
                else:
                    st.caption("No exceptions yet.")

            with st.expander("Evidence", expanded=False):
                st.write(process.get("evidence", []))

