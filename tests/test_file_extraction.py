from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from extractors.files import extract_file_text


class ExcelExtractionTests(unittest.TestCase):
    def test_xlsx_cells_are_extracted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.xlsx"
            with ZipFile(path, "w") as archive:
                archive.writestr(
                    "xl/sharedStrings.xml",
                    '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                    "<si><t>Project</t></si><si><t>Owner</t></si><si><t>OrgMeter</t></si>"
                    "</sst>",
                )
                archive.writestr(
                    "xl/worksheets/sheet1.xml",
                    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                    "<sheetData><row r=\"1\"><c t=\"s\"><v>0</v></c><c t=\"s\"><v>1</v></c></row>"
                    "<row r=\"2\"><c t=\"s\"><v>2</v></c><c><v>42</v></c></row></sheetData>"
                    "</worksheet>",
                )
            text = extract_file_text(path)
            self.assertIn("Project\tOwner", text)
            self.assertIn("OrgMeter\t42", text)


if __name__ == "__main__":
    unittest.main()
