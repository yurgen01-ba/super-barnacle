from __future__ import annotations

import base64
import hashlib
import io
from pathlib import Path
from PIL import Image, ImageFilter


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


def favicon_image() -> Image.Image:
    """Return a thick black logo contour on a transparent background."""
    source = Image.open(LOGO_PATH).convert("L")
    alpha = source.point(lambda value: 255 if value > 72 else 0)
    alpha = alpha.filter(ImageFilter.MaxFilter(9))
    bounds = alpha.getbbox()
    if bounds:
        alpha = alpha.crop(bounds)
    side = max(alpha.size) + 96
    canvas = Image.new("L", (side, side), 0)
    canvas.paste(alpha, ((side - alpha.width) // 2, (side - alpha.height) // 2))
    canvas = canvas.resize((128, 128), Image.Resampling.LANCZOS)
    icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    icon.putalpha(canvas)
    return icon


def favicon_data_uri() -> str:
    """Return the transparent seal mark as an embeddable PNG."""
    buffer = io.BytesIO()
    favicon_image().save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


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
    "settings": '<path d="M19.14 12.94c.04-.31.06-.63.06-.94s-.02-.63-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96a7.2 7.2 0 0 0-1.62-.94l-.36-2.54a.49.49 0 0 0-.48-.41h-3.84a.48.48 0 0 0-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.48.48 0 0 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.31-.09.65-.09.94s.02.63.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58ZM12 15.6A3.6 3.6 0 1 1 12 8.4a3.6 3.6 0 0 1 0 7.2Z" fill-rule="evenodd"/>',
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
