# UI v2 Legacy Boundary

## Goal

`ui_v2/` is the product shell and page routing layer.

`ui/` remains a component library for legacy source importers and low-level viewers until they are migrated.

## Rules

1. New product pages go into `ui_v2/pages/`.
2. New page routing goes through `ui_v2/pages/page_registry.py`.
3. Calls into legacy `ui/` modules must go through `ui_v2/adapters/`.
4. Do not import legacy source tabs directly from `ui_v2/pages/`.
5. Keep `ui/` reusable and side-effect-light.

## Current adapters

- `ui_v2/adapters/source_adapters.py`
- `ui_v2/adapters/project_model_adapters.py`
- `ui_v2/adapters/artifact_adapters.py`
- `ui_v2/adapters/job_status_adapter.py`
