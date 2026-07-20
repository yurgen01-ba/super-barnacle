from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from extractors.files import extract_file_text


class FileExtractorTests(unittest.TestCase):
    def test_extracts_utf8_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.txt"
            path.write_text("Проектное решение", encoding="utf-8")
            self.assertEqual(extract_file_text(path), "Проектное решение")

    def test_extracts_docx_without_optional_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "brief.docx"
            with ZipFile(path, "w") as archive:
                archive.writestr(
                    "word/document.xml",
                    """<?xml version="1.0" encoding="UTF-8"?>
                    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                      <w:body><w:p><w:r><w:t>Project brief</w:t></w:r></w:p></w:body>
                    </w:document>""",
                )
            self.assertEqual(extract_file_text(path), "Project brief")

    def test_rejects_unknown_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.bin"
            path.write_bytes(b"data")
            with self.assertRaises(ValueError):
                extract_file_text(path)


if __name__ == "__main__":
    unittest.main()
