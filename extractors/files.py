from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from pypdf import PdfReader


TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".yaml", ".yml"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | {".pdf", ".docx", ".xlsx", ".pptx"}


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1251", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _xml_text(xml_bytes: bytes, separator: str = " ") -> str:
    root = ElementTree.fromstring(xml_bytes)
    values = [node.text for node in root.iter() if node.tag.endswith("}t") and node.text]
    return separator.join(values).strip()


def _extract_docx(path: Path) -> str:
    with ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    paragraphs = []
    for paragraph in root.iter():
        if not paragraph.tag.endswith("}p"):
            continue
        text = "".join(
            node.text or "" for node in paragraph.iter() if node.tag.endswith("}t")
        ).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _extract_xlsx(path: Path) -> str:
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root:
                shared.append("".join(
                    node.text or "" for node in item.iter() if node.tag.endswith("}t")
                ))

        lines = []
        sheet_names = sorted(
            name for name in names
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )
        for sheet_name in sheet_names:
            root = ElementTree.fromstring(archive.read(sheet_name))
            for row in (node for node in root.iter() if node.tag.endswith("}row")):
                cells = []
                for cell in (node for node in row if node.tag.endswith("}c")):
                    value_node = next(
                        (node for node in cell.iter() if node.tag.endswith("}v")),
                        None,
                    )
                    value = value_node.text if value_node is not None else ""
                    if cell.attrib.get("t") == "s" and value.isdigit():
                        index = int(value)
                        value = shared[index] if index < len(shared) else value
                    cells.append(value)
                if any(cells):
                    lines.append("\t".join(cells))
    return "\n".join(lines)


def _extract_pptx(path: Path) -> str:
    with ZipFile(path) as archive:
        slides = sorted(
            name for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
        return "\n\n".join(
            _xml_text(archive.read(name)) for name in slides
        ).strip()


def extract_file_text(path: str | Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")
    if suffix in TEXT_EXTENSIONS:
        text = _decode_text(path.read_bytes())
        if suffix == ".json":
            try:
                return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
            except Exception:
                return text
        if suffix == ".csv":
            rows = csv.reader(io.StringIO(text))
            return "\n".join("\t".join(row) for row in rows)
        return text
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix == ".xlsx":
        return _extract_xlsx(path)
    if suffix == ".pptx":
        return _extract_pptx(path)
    raise ValueError(f"Unsupported file type: {suffix}")
