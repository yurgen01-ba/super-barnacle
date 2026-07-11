from __future__ import annotations

from ui.actors import render_actors_tab
from ui.domain_model import render_domain_model_tab
from ui.entities import render_entities_tab
from ui.facts import render_facts_tab
from ui.memory import render_memory_tab
from ui.ontology import render_ontology_tab
from ui.processes import render_processes_tab
from ui.project_intelligence import render_project_intelligence_tab
from ui.project_summary import render_project_summary_tab
from ui.relationships import render_relationships_tab


def _no_repo(fn):
    return lambda memory_repository: fn()


def _with_repo(fn):
    return lambda memory_repository: fn(memory_repository)


PROJECT_MODEL_TABS = [
    {"label": "🚀 Refresh", "render": _no_repo(render_project_intelligence_tab)},
    {"label": "📌 Summary", "render": _no_repo(render_project_summary_tab)},
    {"label": "🏛️ Domain", "render": _no_repo(render_domain_model_tab)},
    {"label": "👥 Actors", "render": _no_repo(render_actors_tab)},
    {"label": "🗺️ Processes", "render": _no_repo(render_processes_tab)},
    {"label": "🧬 Ontology", "render": _no_repo(render_ontology_tab)},
    {"label": "🧠 Knowledge", "render": _with_repo(render_memory_tab)},
    {"label": "🧩 Facts", "render": _no_repo(render_facts_tab)},
    {"label": "🕸️ Entities", "render": _no_repo(render_entities_tab)},
    {"label": "🔗 Relationships", "render": _no_repo(render_relationships_tab)},
]
