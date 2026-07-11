import streamlit as st

from repositories.memory_repository import MemoryRepository
from ui.actors import render_actors_tab
from ui.design import render_hero
from ui.domain_model import render_domain_model_tab
from ui.entities import render_entities_tab
from ui.facts import render_facts_tab
from ui.memory import render_memory_tab
from ui.ontology import render_ontology_tab
from ui.processes import render_processes_tab
from ui.project_intelligence import render_project_intelligence_tab
from ui.project_summary import render_project_summary_tab
from ui.relationships import render_relationships_tab


def render_project_model_area(memory_repository: MemoryRepository):
    render_hero(
        title="Project Model",
        caption="Living model of the project: summary, domain objects, actors, processes, facts, relationships and evidence.",
        pills=[
            "Project Intelligence",
            "Evidence-based",
            "Model-first AI Analyst",
        ],
    )

    (
        tab_refresh,
        tab_summary,
        tab_domain,
        tab_actors,
        tab_processes,
        tab_ontology,
        tab_memory,
        tab_facts,
        tab_entities,
        tab_relationships,
    ) = st.tabs(
        [
            "🚀 Refresh",
            "📌 Summary",
            "🏛️ Domain",
            "👥 Actors",
            "🗺️ Processes",
            "🧬 Ontology",
            "🧠 Knowledge",
            "🧩 Facts",
            "🕸️ Entities",
            "🔗 Relationships",
        ]
    )

    with tab_refresh:
        render_project_intelligence_tab()

    with tab_summary:
        render_project_summary_tab()

    with tab_domain:
        render_domain_model_tab()

    with tab_actors:
        render_actors_tab()

    with tab_processes:
        render_processes_tab()

    with tab_ontology:
        render_ontology_tab()

    with tab_memory:
        render_memory_tab(memory_repository)

    with tab_facts:
        render_facts_tab()

    with tab_entities:
        render_entities_tab()

    with tab_relationships:
        render_relationships_tab()

