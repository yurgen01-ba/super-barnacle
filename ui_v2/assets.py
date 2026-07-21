from __future__ import annotations

import base64
import hashlib
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "project-brain-logo.png"


def file_data_uri(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def logo_data_uri() -> str:
    return file_data_uri(LOGO_PATH)


def svg_data_uri(name: str) -> str:
    path = ASSETS_DIR / f"{name}.svg"
    if not path.exists():
        return ""
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


_NAV_ICONS = {
    "projects": '<path d="M5 4h6v6H5zM13 4h6v6h-6zM5 12h6v8H5zM13 12h6v8h-6z"/>',
    "workspace": '<path d="M3 11 12 4l9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "sources": '<path d="M5 5h14v3H5zM5 10.5h14v3H5zM5 16h14v3H5z"/>',
    "participants": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-4 2-7 6-7s6 3 6 7zM14 14c4 0 7 2 7 6h-5c0-2-.7-4-2-6z"/>',
    "speech": '<path d="M12 3a6 6 0 0 0-6 6v2a6 6 0 0 0 12 0V9a6 6 0 0 0-6-6Zm-9 8h2a7 7 0 0 0 14 0h2a9 9 0 0 1-8 8.94V22h-2v-2.06A9 9 0 0 1 3 11Z"/>',
    "artifacts": '<path d="M4 3h11l5 5v13H4zM14 4v5h5M8 13h8M8 17h8" fill="none" stroke="currentColor" stroke-width="2"/>',
    "exports": '<path d="M11 3h2v11l4-4 1.5 1.5L12 18l-6.5-6.5L7 10l4 4zM4 20h16v2H4z"/>',
    "meetings": '<path d="M4 5h16v15H4zM7 2h2v6H7zM15 2h2v6h-2zM7 11h4v3H7zM13 11h4v3h-4z"/>',
    "files": '<path d="M5 2h9l5 5v15H5zM13 3v6h5" fill="none" stroke="currentColor" stroke-width="2"/>',
    "settings": '<path d="m12 2 2 3 4-.3.8 3.9 3.2 2-2 3.4 1.2 3.8-3.8 1.2-2 3.2-3.4-2-3.4 2-2-3.2-3.8-1.2L6 14l-2-3.4 3.2-2L8 4.7l4 .3z"/><circle cx="12" cy="12" r="3" fill="#0A0A0B"/>',
    "model": '<path d="M12 2 3 7v10l9 5 9-5V7zM3.5 7 12 12l8.5-5M12 12v10" fill="none" stroke="currentColor" stroke-width="2"/>',
}


def nav_icon_data_uri(name: str) -> str:
    body = _NAV_ICONS.get(name, _NAV_ICONS["files"])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">{body}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def default_avatar_data_uri(name: str) -> str:
    clean_name = " ".join(str(name or "User").split())
    initials = "".join(part[0] for part in clean_name.split()[:2]).upper() or "U"
    digest = hashlib.sha256(clean_name.encode("utf-8")).hexdigest()
    palette = ["#EF4444", "#8B5CF6", "#0EA5E9", "#14B8A6", "#F59E0B", "#EC4899"]
    color = palette[int(digest[:2], 16) % len(palette)]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">'
        f'<rect width="128" height="128" rx="64" fill="{color}"/>'
        f'<text x="64" y="76" text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="42" font-weight="700" fill="white">{initials}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
