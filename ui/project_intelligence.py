import time

import streamlit as st

from builders.actors_builder import ActorsBuilder
from builders.domain_model_builder import DomainModelBuilder
from builders.entity_builder import EntityBuilder
from builders.ontology_builder import OntologyBuilder
from builders.process_builder import ProcessBuilder
from builders.project_summary_builder import ProjectSummaryBuilder
from builders.relationship_builder import RelationshipBuilder
from repositories.actors_repository import ActorsRepository
from repositories.domain_model_repository import DomainModelRepository
from repositories.entity_repository import EntityRepository
from repositories.fact_repository import FactRepository
from repositories.ontology_repository import OntologyRepository
from repositories.process_repository import ProcessRepository
from repositories.project_repository import ProjectRepository
from repositories.relationship_repository import RelationshipRepository


DEFAULT_PIPELINE_STEPS = [
    "entities",
    "relationships",
    "ontology",
    "domain_model",
    "actors",
    "processes",
    "project_summary",
]


STEP_LABELS = {
    "entities": "Entities",
    "relationships": "Relationships",
    "ontology": "Ontology",
    "domain_model": "Domain Model",
    "actors": "Actors",
    "processes": "Processes",
    "project_summary": "Project Summary",
}


def _run_step(step_name: str, *, summary_model: str, summary_host: str, summary_timeout: int):
    if step_name == "entities":
        return EntityBuilder().build_entities_from_facts()

    if step_name == "relationships":
        return RelationshipBuilder().build_relationships_from_facts()

    if step_name == "ontology":
        return OntologyBuilder().classify_entities()

    if step_name == "domain_model":
        return DomainModelBuilder().build_domain_model()

    if step_name == "actors":
        return ActorsBuilder().build_actors()

    if step_name == "processes":
        return ProcessBuilder().build_processes()

    if step_name == "project_summary":
        return ProjectSummaryBuilder(
            model=summary_model,
            host=summary_host,
            timeout_seconds=summary_timeout,
        ).build_and_save_summary()

    raise ValueError(f"Unknown Project Intelligence step: {step_name}")


def _collect_statistics():
    stats = {}

    try:
        stats["facts"] = FactRepository().get_fact_counts()
    except Exception as exc:
        stats["facts_error"] = repr(exc)

    try:
        stats["entities"] = len(EntityRepository().list_entities(limit=10000))
    except Exception as exc:
        stats["entities_error"] = repr(exc)

    try:
        stats["relationships"] = len(RelationshipRepository().list_relationships(limit=10000))
    except Exception as exc:
        stats["relationships_error"] = repr(exc)

    try:
        stats["ontology"] = OntologyRepository().get_ontology_counts()
    except Exception as exc:
        stats["ontology_error"] = repr(exc)

    try:
        stats["domain_model"] = DomainModelRepository().get_domain_model_statistics()
    except Exception as exc:
        stats["domain_model_error"] = repr(exc)

    try:
        stats["actors"] = ActorsRepository().get_actor_statistics()
    except Exception as exc:
        stats["actors_error"] = repr(exc)

    try:
        stats["processes"] = ProcessRepository().get_process_statistics()
    except Exception as exc:
        stats["processes_error"] = repr(exc)

    try:
        stats["project_model"] = ProjectRepository().get_model_statistics()
    except Exception as exc:
        stats["project_model_error"] = repr(exc)

    return stats


def render_project_intelligence_tab():
    st.header("Project Intelligence Refresh")
    st.caption(
        "Run the current Project Model builders in the correct order. This is a lightweight bridge before the full Builder Registry/Pipeline refactor."
    )

    with st.expander("Pipeline settings", expanded=False):
        selected_steps = st.multiselect(
            "Steps",
            options=DEFAULT_PIPELINE_STEPS,
            default=DEFAULT_PIPELINE_STEPS,
            format_func=lambda step: STEP_LABELS.get(step, step),
            key="project_intelligence_steps",
        )

        col1, col2 = st.columns(2)
        with col1:
            summary_model = st.selectbox(
                "Summary model",
                options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
                index=0,
                key="project_intelligence_summary_model",
            )
        with col2:
            summary_timeout = st.slider(
                "Summary timeout, seconds",
                120,
                600,
                300,
                30,
                key="project_intelligence_summary_timeout",
            )

        summary_host = st.text_input(
            "Ollama host",
            value="http://localhost:11434",
            key="project_intelligence_summary_host",
        )

        stop_on_error = st.checkbox(
            "Stop on first error",
            value=False,
            key="project_intelligence_stop_on_error",
            help="Disabled by default so one failed layer does not block later diagnostics.",
        )

    with st.expander("Current model statistics", expanded=True):
        st.write(_collect_statistics())

    if not selected_steps:
        st.warning("Select at least one step.")
        return

    if st.button("Refresh Project Intelligence", key="refresh_project_intelligence", width="stretch"):
        progress = st.progress(0)
        status_box = st.empty()
        result_box = st.container()

        results = []
        total = len(selected_steps)

        for index, step_name in enumerate(selected_steps, start=1):
            label = STEP_LABELS.get(step_name, step_name)
            started_at = time.time()

            status_box.info(f"Running {label} ({index}/{total})...")

            try:
                result = _run_step(
                    step_name,
                    summary_model=summary_model,
                    summary_host=summary_host,
                    summary_timeout=summary_timeout,
                )
                elapsed = round(time.time() - started_at, 2)
                results.append({
                    "step": step_name,
                    "label": label,
                    "status": "completed",
                    "elapsed_seconds": elapsed,
                    "result": result,
                })
                status_box.success(f"Completed {label} in {elapsed}s")

            except Exception as exc:
                elapsed = round(time.time() - started_at, 2)
                error = repr(exc)
                results.append({
                    "step": step_name,
                    "label": label,
                    "status": "failed",
                    "elapsed_seconds": elapsed,
                    "error": error,
                })
                status_box.error(f"Failed {label}: {error}")

                if stop_on_error:
                    break

            progress.progress(min(index / total, 1.0))

        with result_box:
            st.subheader("Refresh result")
            st.write(results)

            st.subheader("Updated model statistics")
            st.write(_collect_statistics())

