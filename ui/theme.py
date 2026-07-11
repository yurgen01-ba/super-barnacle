from __future__ import annotations

import streamlit as st

from ui.component_styles import apply_component_styles
from ui.dark_theme import apply_complete_dark_theme
from ui.design_tokens import apply_design_tokens


def apply_project_brain_theme():
    """
    Single entry point for Project Brain UI styling.

    Use this once near app startup.
    """
    apply_design_tokens()
    apply_complete_dark_theme()
    apply_component_styles()
