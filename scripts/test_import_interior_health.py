"""Guards for source-specific ambiguity and omission failures in the IH importer."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("interior_import", Path(__file__).with_name("import-interior-health-salaries.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class InteriorHealthImportTests(unittest.TestCase):
    def test_missing_zero_and_negative_expenses_are_distinct(self):
        self.assertIsNone(mod.amount("-"))
        self.assertEqual(mod.amount("0"), 0)
        self.assertEqual(mod.amount("-      145"), -145)
        self.assertEqual(mod.amount("(1,668)*"), -1668)

    def test_unexpected_money_not_silently_cleaned(self):
        for token in ("", "1O0", "1,23", "(100", "-", "- - 145", "0.00"):
            if token == "-":
                continue
            with self.subTest(token=token), self.assertRaises(ValueError):
                mod.amount(token)

    def test_published_name_and_negative_marker(self):
        row = mod.parse_row("YAKIMOV,MARGARET (PEGGY)    117,339    - 486", 88, 2018)
        self.assertEqual(row, ["interior-health", "YAKIMOV,MARGARET (PEGGY)", None, 117339, -486, 88])

    def test_threshold_exception_cannot_admit_other_rows(self):
        self.assertEqual(mod.parse_row("BAXTER,LOUISE M    75,000    -", 8, 2021), mod.BOUNDARY_ROWS[2021][0])
        for line, page, end in (("OTHER,NAME    75,000    -", 8, 2021),
                                ("BAXTER,LOUISE M    75,000    -", 9, 2021),
                                ("BAXTER,LOUISE M    75,000    -", 8, 2022),
                                ("BAXTER,LOUISE M    74,999    -", 8, 2021)):
            with self.subTest(line=line, page=page, end=end), self.assertRaises(ValueError):
                mod.parse_row(line, page, end)

    def _document(self):
        return ("Schedule of Employee Remuneration and Expenses\n"
                "For the Year Ending March 31, 2025\n"
                "EMPLOYEE NAME     REMUNERATION    EXPENSES\n"
                "EXAMPLE,NAME      80,000          -\n"
                "Total Greater than $75,000        $ 80,000     $ 0\n"
                "Total Less than or equal to $75,000  20,000     100\n"
                "Grand Total                       $ 100,000   $ 100\n"
                "Page 1 of 1\n\f")

    def test_aggregate_values_are_not_employee_rows(self):
        rows, controls = mod.parse_layout(self._document(), 2025)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], None)
        self.assertEqual(controls["underThresholdRemunerationExcluded"], 20000)

    def test_wrong_period_or_missing_page_footer_fails(self):
        with self.assertRaises(ValueError):
            mod.parse_layout(self._document(), 2024)
        with self.assertRaises(ValueError):
            mod.parse_layout(self._document().replace("Page 1 of 1", "Page 2 of 2"), 2025)

    def test_omitted_or_unreadable_employee_line_fails(self):
        text = self._document().replace("EXAMPLE,NAME      80,000          -", "EXAMPLE,NAME      unreadable          -")
        with self.assertRaises(ValueError):
            mod.parse_layout(text, 2025)

    def test_conflicting_grand_total_fails(self):
        text = self._document().replace("$ 100,000", "$ 999,999")
        with self.assertRaises(ValueError):
            mod.parse_layout(text, 2025)


if __name__ == "__main__":
    unittest.main()
