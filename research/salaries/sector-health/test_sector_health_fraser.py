"""Regression checks for the recovered historical Fraser source layouts."""
import subprocess
import unittest
from pathlib import Path

from sector_health_fraser import amount, parse_layout, independent_rows, REVIEWED


class HistoricalFraser(unittest.TestCase):
    def test_missing_zero_negative_remain_distinct(self):
        self.assertIsNone(amount("-"))
        self.assertEqual(amount("0"), 0)
        self.assertEqual(amount("(5)"), -5)
        self.assertEqual(amount("1,234"), 1234)
        with self.assertRaises(ValueError):
            amount("1,23")

    def test_full_originals_with_independent_engine(self):
        for end in REVIEWED:
            pdf = Path(f"/tmp/sector-health/fraser-{end}.pdf")
            if not pdf.exists():
                self.skipTest("Original PDF cache is needed for integration verification")
            text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
            rows, val = parse_layout(text, end)
            self.assertEqual(rows, independent_rows(pdf, end))
            self.assertEqual(len(rows), REVIEWED[end]["totals"][0])

    def test_reject_wrong_period_header(self):
        pdf = Path("/tmp/sector-health/fraser-2014.pdf")
        if not pdf.exists():
            self.skipTest("Original PDF cache is needed for mutation verification")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        with self.assertRaises(AssertionError):
            parse_layout(text.replace("FOR THE FISCAL YEAR ENDED MARCH 31, 2014", "FOR THE FISCAL YEAR ENDED MARCH 31, 2015", 1), 2014)

    def test_reject_dropped_employee_cell(self):
        pdf = Path("/tmp/sector-health/fraser-2015.pdf")
        if not pdf.exists():
            self.skipTest("Original PDF cache is needed for mutation verification")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        with self.assertRaises(AssertionError):
            parse_layout(text.replace("AAL,AMANDEEP", "MALFORMED ROW", 1), 2015)

    def test_physical_page_offset_not_printed_footer(self):
        pdf = Path("/tmp/sector-health/fraser-2014.pdf")
        if not pdf.exists():
            self.skipTest("Original PDF cache is needed for page verification")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        rows, val = parse_layout(text, 2014)
        self.assertEqual(rows[0][5], 2)
        self.assertEqual(rows[-1][5], 118)
        self.assertEqual(val["rowsPerPhysicalPage"][0], 0)
        self.assertEqual(len(rows), val["sourceDeclaredNamedCount"])

    def test_expense_recovery_and_source_totals_unchanged(self):
        pdf = Path("/tmp/sector-health/fraser-2014.pdf")
        if not pdf.exists():
            self.skipTest("Original PDF cache is needed for monetary verification")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        rows, val = parse_layout(text, 2014)
        self.assertIn(["fraser-health", "LUCKEN,BRENDA A", None, 91313, -5, 64], rows)
        self.assertEqual(sum(r[3] for r in rows) - val["printedNamedRemuneration"], 40)
        self.assertEqual(sum(r[4] or 0 for r in rows) - val["printedNamedExpenses"], 34)


if __name__ == "__main__":
    unittest.main()
