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
