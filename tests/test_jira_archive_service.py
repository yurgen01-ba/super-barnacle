import io
import shutil
import unittest
from pathlib import Path
from zipfile import ZipFile

from services.jira_archive_service import MAX_JIRA_PDFS, stage_jira_uploads

import py7zr


class FakeUpload:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getbuffer(self):
        return memoryview(self._data)


def make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def make_7z(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with py7zr.SevenZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(data, name)
    return buffer.getvalue()


class JiraArchiveServiceTests(unittest.TestCase):
    def setUp(self):
        self.staged_dirs = []

    def tearDown(self):
        for directory in self.staged_dirs:
            shutil.rmtree(directory, ignore_errors=True)

    def _track(self, specs):
        self.staged_dirs.extend({str(Path(spec["path"]).parent) for spec in specs})
        return specs

    def test_stages_pdfs_from_zip_and_ignores_other_files(self):
        archive = make_zip({"tickets/ABC-1.pdf": b"pdf1", "notes.txt": b"skip"})
        specs = self._track(stage_jira_uploads([FakeUpload("jira.zip", archive)]))
        self.assertEqual([spec["name"] for spec in specs], ["ABC-1.pdf"])

    def test_stages_pdfs_from_7z(self):
        archive = make_7z({"tickets/ABC-2.pdf": b"pdf2", "notes.txt": b"skip"})
        specs = self._track(stage_jira_uploads([FakeUpload("jira.7z", archive)]))
        self.assertEqual([spec["name"] for spec in specs], ["ABC-2.pdf"])

    def test_rejects_more_than_twenty_pdfs(self):
        files = {f"ticket-{index}.pdf": b"pdf" for index in range(MAX_JIRA_PDFS + 1)}
        with self.assertRaisesRegex(ValueError, "больше 20"):
            stage_jira_uploads([FakeUpload("jira.zip", make_zip(files))])

    def test_rejects_archive_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "Небезопасный путь"):
            stage_jira_uploads([FakeUpload("jira.zip", make_zip({"../ticket.pdf": b"pdf"}))])

    def test_enforces_combined_limit_for_direct_pdfs(self):
        uploads = [FakeUpload(f"ticket-{index}.pdf", b"pdf") for index in range(MAX_JIRA_PDFS + 1)]
        with self.assertRaisesRegex(ValueError, "не более 20"):
            stage_jira_uploads(uploads)


if __name__ == "__main__":
    unittest.main()
