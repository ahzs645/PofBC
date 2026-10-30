"""Regression checks against the retained, reviewed BC Transit OCR evidence."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bc_transit", ROOT / "scripts/extract-bc-transit-salaries.py")
transit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transit)
OUT = ROOT / "research/salaries/bc-transit"
REVIEWS = json.loads((OUT / "review/annual-reviews.json").read_text())["sources"]


def source_fixture(slug="2019-20"):
    review = copy.deepcopy(next(r for r in REVIEWS if r["slug"] == slug))
    evidence = (OUT / "review" / review["rawOcrFile"]).read_bytes()
    if transit.sha(evidence) != review["rawOcrSha256"]:
        raise AssertionError("Reviewed fixture hash changed")
    return review, json.loads(gzip.decompress(evidence))


class TransitExtractionTests(unittest.TestCase):
    def test_saved_ocr_passes_match_every_published_row_and_source_hash(self):
        for source in REVIEWS:
            if source["method"] != "reviewed-ocr":
                continue
            with self.subTest(year=source["slug"]):
                review, raw = source_fixture(source["slug"])
                published = json.loads(gzip.decompress((OUT / f"{source['slug']}.json.gzip").read_bytes()))
                for pass_id in ["300", "400"]:
                    self.assertEqual(transit.parse_annual_pages(raw[pass_id], review, pass_id), published)
                normalized = json.dumps(published, ensure_ascii=False, separators=(",", ":")).encode()
                self.assertEqual(transit.sha(normalized), review["normalizedSha256"])

    def test_wrong_year_in_a_repeated_page_header_is_rejected(self):
        review, raw = source_fixture("2015-16")
        raw["300"]["8"] = raw["300"]["8"].replace("March 31, 2016", "March 31, 2015")
        with self.assertRaisesRegex(ValueError, "Wrong employee schedule year"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_wrong_first_page_period_is_rejected(self):
        review, raw = source_fixture()
        raw["300"]["6"] = raw["300"]["6"].replace("March 31, 2020", "March 31, 2021")
        with self.assertRaisesRegex(ValueError, "threshold or period"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_missing_employee_page_is_rejected(self):
        review, raw = source_fixture()
        del raw["300"]["8"]
        with self.assertRaisesRegex(ValueError, "Incomplete annual employee page set"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_one_dollar_error_is_rejected_even_inside_rounding_bound(self):
        review, raw = source_fixture()
        raw["300"]["6"] = raw["300"]["6"].replace("84,377 231", "84,378 231")
        with self.assertRaisesRegex(ValueError, "differs from reviewed evidence"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_missing_row_is_rejected(self):
        review, raw = source_fixture()
        raw["300"]["6"] = raw["300"]["6"].replace("Ages, Mark 101,764 -\n", "")
        with self.assertRaisesRegex(ValueError, "differs from reviewed evidence"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_changed_named_subtotal_is_rejected(self):
        review, raw = source_fixture()
        raw["300"]["12"] = raw["300"]["12"].replace("33,190,139", "33,190,140")
        with self.assertRaisesRegex(ValueError, "Printed Over 75,000 Remuneration"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_stale_ocr_correction_is_rejected(self):
        review, raw = source_fixture()
        review["reviewedCorrections"]["300"].append({
            "pdfPage": 6, "ocrLine": "Absent old OCR text", "verifiedLine": "Not a source record",
        })
        with self.assertRaisesRegex(ValueError, "correction was not used"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_printed_name_without_comma_is_retained_only_when_reviewed(self):
        review, raw = source_fixture("2025-26")
        rows = transit.parse_annual_pages(raw["300"], review, "300")
        self.assertIn(["bc-transit", "Parminder Singh", None, 116736, 0, 20], rows)
        review["namesWithoutComma"] = []
        with self.assertRaisesRegex(ValueError, "Unreviewed name structure"):
            transit.parse_annual_pages(raw["300"], review, "300")

    def test_reimport_does_not_erase_other_accepted_years(self):
        original = json.loads((OUT / "sources.json").read_text())
        source = next(s for s in original["sources"] if s["slug"] == "2020-21")
        content = (OUT / source["file"]).read_bytes()
        with tempfile.TemporaryDirectory() as folder, patch.object(transit, "OUT", Path(folder)):
            path = Path(folder) / "sources.json"
            path.write_text(json.dumps(original))
            transit.write_source(source, content)
            rebuilt = json.loads(path.read_text())
            self.assertEqual(rebuilt["sources"], sorted(original["sources"], key=lambda s: s["slug"]))


if __name__ == "__main__":
    unittest.main()
