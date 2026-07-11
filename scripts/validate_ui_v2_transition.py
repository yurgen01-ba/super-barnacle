from __future__ import annotations

import importlib

MODULES = [
    "ui_v2.app_shell",
    "ui_v2.pages.page_registry",
    "ui_v2.pages.dashboard",
    "ui_v2.pages.sources",
    "ui_v2.pages.artifacts",
    "ui_v2.pages.project_model",
    "ui_v2.pages.settings",
    "ui_v2.adapters.source_adapters",
    "ui_v2.adapters.project_model_adapters",
    "ui_v2.adapters.artifact_adapters",
    "ui_v2.adapters.job_status_adapter",
]


def main():
    failed = []
    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
            print(f"OK: {module_name}")
        except Exception as exc:
            failed.append((module_name, repr(exc)))
            print(f"FAIL: {module_name}: {repr(exc)}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
