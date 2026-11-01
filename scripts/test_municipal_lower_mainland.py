#!/usr/bin/env python3
"""Focused offline regressions for failure modes observed in municipal SOFI PDFs."""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from parse_municipal_lower_mainland import normalize, parse_reviewed, table_completeness
from parse_municipal_lower_mainland_layouts import key, money, split_amounts


class LowerMainlandParserTests(unittest.TestCase):
    def test_separately_printed_negative_is_not_a_name_or_missing_cell(self):
        prefix, amounts = split_amounts("Atkins,Christopher T    132,216.94 -     900.11 593.67", 3)
        self.assertEqual(prefix, "Atkins,Christopher T")
        self.assertEqual(amounts, ["132,216.94", "-900.11", "593.67"])

    def test_source_missing_zero_and_negative_remain_distinct(self):
        self.assertIsNone(money("‐"))
        self.assertEqual(money("0"), Decimal(0))
        self.assertEqual(money("(123.45)"), Decimal("-123.45"))

    def test_total_including_expenses_is_never_treated_as_pay(self):
        reviewed = {"key": "test", "employerSlug": "test", "remunerationColumns": [0], "expensesColumn": 1}
        rows = [{"name": "Disclosed Name", "position": None, "raw": ["100,000", "5,000", "105,000"], "page": 2}]
        self.assertEqual(normalize(rows, reviewed)[0][3:5], [100000, 5000])

    def test_compensation_components_and_missing_expenses(self):
        reviewed = {"key": "test", "employerSlug": "test", "remunerationColumns": [0, 1], "expensesColumn": 2}
        rows = [{"name": "Published, I", "position": None, "raw": ["100,000", "4,500", "-"], "page": 7}]
        self.assertEqual(normalize(rows, reviewed), [["test", "Published, I", None, 104500, None, 7]])

    def test_all_missing_remuneration_fails_closed(self):
        reviewed = {"key": "test", "employerSlug": "test", "remunerationColumns": [0, 1], "expensesColumn": 2}
        with self.assertRaisesRegex(ValueError, "missing all remuneration"):
            normalize([{"name": "A", "position": None, "raw": ["-", "-", "40"], "page": 1}], reviewed)

    def test_completeness_catches_wrapped_position_omission(self):
        text = "A, B   Chief Administrative  100,000  10\nOfficer\nC, D   Clerk  90,000  20"
        parsed = {"rows": [{"name": "A, B", "page": 1, "sourceKey": key("A, B Chief Administrative 100,000 10")},
                           {"name": "C, D", "page": 1, "sourceKey": key("C, D Clerk 90,000 20")}]}
        self.assertEqual(table_completeness(parsed, text), [{"page": 1, "text": "Officer"}])

    def test_completeness_catches_omitted_employee_row(self):
        text = "A 100,000 10\nB 90,000 20\nC 80,000 30"
        parsed = {"rows": [{"name": "A", "page": 1, "sourceKey": key("A 100,000 10")},
                           {"name": "C", "page": 1, "sourceKey": key("C 80,000 30")}]}
        self.assertEqual(table_completeness(parsed, text), [{"page": 1, "text": "B90,00020"}])

    def test_changed_source_fails_before_pdf_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / "changed-2025.pdf").write_bytes(b"%PDF-an-unreviewed-replacement")
            with self.assertRaisesRegex(ValueError, "original PDF hash changed"):
                parse_reviewed({"key": "changed-2025", "sha256": "0" * 64}, cache)


if __name__ == "__main__":
    unittest.main()
