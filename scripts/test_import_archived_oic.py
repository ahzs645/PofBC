"""Regression checks for OIC source boundaries, sparse cells and guarded overlap review."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("archived_oic", Path(__file__).with_name("import-archived-oic-salaries.py"))
oic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oic)


class FakePage:
    class Rectangle:
        width = 612
    rect = Rectangle()

    def __init__(self, words):
        self.words = words

    def get_text(self, mode):
        assert mode == "words"
        return self.words


def word(x, y, text):
    return (x, y, x + len(text) * 3, y + 8, text, 0, 0, 0)


class OICImportTests(unittest.TestCase):
    def test_negative_blank_and_below_threshold_payments(self):
        raw = "OIC and Other Appointees\n$ $\nFRANK,ERIN\nCorrespondence Clerk (242)\nALPHA,A\nSupport Staff 49\nBETA,B\nPublic Affairs Officer\n"
        self.assertEqual(oic.parse_raw_page(raw, True), [
            ["FRANK,ERIN", "Correspondence Clerk", -242],
            ["ALPHA,A", "Support Staff", 49], ["BETA,B", "Public Affairs Officer", None]])

    def test_original_name_punctuation_and_missing_positions(self):
        self.assertEqual(oic.parse_raw_page("Header\n$ $\nVAN BLARCOM,JOHN DAVID 109,894\n", False),
                         [["VAN BLARCOM,JOHN DAVID", None, 109894]])

    def test_truncated_position_record_fails(self):
        with self.assertRaisesRegex(ValueError, "Truncated"):
            oic.parse_raw_page("Header\n$\nALPHA,A\n", True)

    def test_shifted_table_gutter_keeps_columns_separate(self):
        # 2015/16 alternating pages shift by 14 points. A fixed x=315 gutter
        # incorrectly attaches the right-column name to the left-column name.
        page = FakePage([word(271, 90, "$"), word(523, 90, "$"),
                         word(55, 102, "ALPHA,A"), word(59, 112, "Judge"), word(266, 112, "247,447"),
                         word(307, 102, "BETA,B"), word(311, 112, "Writer"), word(518, 112, "57,231")])
        self.assertEqual(oic.parse_coordinate_page(page, True), [
            ["ALPHA,A", "Judge", 247447], ["BETA,B", "Writer", 57231]])

    def test_numeric_position_is_not_a_positioned_salary_cell(self):
        page = FakePage([word(285, 90, "$"), word(69, 102, "ALPHA,A"),
                         word(73, 112, "Band"), word(93, 112, "2")])
        self.assertEqual(oic.parse_coordinate_page(page, True), [["ALPHA,A", "Band 2", None]])

    def test_invalid_money_fails_and_zero_is_not_missing(self):
        for value in ["1,,234", "1,23", "(242", "242)", "(-242)", "-(242)", "NaN", "Infinity", "", "$42"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                oic.amount(value)
        self.assertEqual(oic.amount("0"), 0)
        self.assertIsNone(oic.amount("Nil"))

    def test_only_enumerated_overlap_is_removed(self):
        existing = {"deputy": [["public-service", "BYNG, DAVID", "Deputy Minister or Associate Deputy Minister", 218581, 37834]]}
        decision = {"name": "BYNG,DAVE", "position": "Associate Deputy Minister", "remuneration": 218581,
                    "physicalPdfPage": 16, "retainedSourceId": "deputy", "retainedName": "BYNG, DAVID",
                    "retainedRemuneration": 218581, "retainedExpenses": 37834}
        rows = [["BYNG,DAVE", "Associate Deputy Minister", 218581, 16], ["BYNG,DAVE", "Different source role", 7000, 17]]
        accepted, _ = oic.reviewed_rows(rows, {"reviewedDuplicatePaymentExclusions": [decision]}, existing)
        self.assertEqual(accepted, [["public-service", "BYNG,DAVE", "Different source role", 7000, None, 17]])
        existing["deputy"][0][3] += 1
        with self.assertRaisesRegex(ValueError, "retained deputy"):
            oic.reviewed_rows(rows, {"reviewedDuplicatePaymentExclusions": [decision]}, existing)

    def test_unreviewed_cross_schedule_duplicate_fails(self):
        rows = [["ALPHA,A", "Deputy Minister", 123456, 15]]
        existing = {"deputy": [["public-service", "ALPHA, A", "Deputy Minister", 123456, None]]}
        with self.assertRaisesRegex(ValueError, "Unreviewed cross-schedule"):
            oic.reviewed_rows(rows, {"reviewedDuplicatePaymentExclusions": []}, existing)

    def test_original_pdf_hash_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / "2006-07.pdf").write_bytes(b"%PDF changed bytes")
            with self.assertRaisesRegex(ValueError, "original PDF changed"):
                oic.read_pdf({"slug": "2006-07", "year": "2006/07", "sha256": "0" * 64,
                              "sourceBytes": 18}, cache, True)


if __name__ == "__main__":
    unittest.main()
