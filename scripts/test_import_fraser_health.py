import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("fraser_health_import", Path(__file__).with_name("import-fraser-health-salaries.py"))
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def schedule(rows="SMITH,JANE  75,000  -", named="75,000  0", below="20,000  10", grand="95,000  10", year=2025):
    return f"""FRASER HEALTH AUTHORITY
SCHEDULE OF EMPLOYEES' REMUNERATION AND EXPENSES
FOR THE FISCAL YEAR ENDED MARCH 31, {year}
EMPLOYEE NAME  REMUNERATION  EXPENSES
{rows}
Total payments equal to or greater than $75,000  {named}
Total payments less than $75,000  {below}
Total payments to all Fraser Health employees  {grand}
1\f"""


class FraserHealthImportTests(unittest.TestCase):
    def test_inclusive_threshold_and_expense_semantics(self):
        self.assertEqual(IMPORTER.parse_row("SMITH,JANE  75,000  -", 3), ["fraser-health", "SMITH,JANE", None, 75000, None, 3])
        self.assertEqual(IMPORTER.parse_row("CANOSA,SANDEE  81,287  ‐    459", 22)[4], -459)
        self.assertEqual(IMPORTER.parse_row("BRAR,RAMAN  126,803  0", 24)[4], 0)
        with self.assertRaises(ValueError):
            IMPORTER.parse_row("SMITH,JANE  74,999  -", 3)
        with self.assertRaises(ValueError):
            IMPORTER.parse_row("SMITH,JANE  75,0O0  -", 3)

    def test_schedule_dates_and_footers_are_checked(self):
        rows, validation = IMPORTER.parse_layout(schedule(), 2025)
        self.assertEqual(len(rows), 1)
        self.assertEqual(validation["rowsPerPhysicalPage"], [1])
        for text in [schedule(year=2024), schedule().replace("1\f", "2\f"), schedule().replace("SMITH,JANE  75,000  -", "GARBLED EMPLOYEE")]:
            with self.assertRaises(ValueError):
                IMPORTER.parse_layout(text, 2025)

    def test_repeated_names_and_records_are_preserved_for_review(self):
        rows, validation = IMPORTER.parse_layout(schedule(
            rows="SMITH,JANE  75,000  -\nSMITH,JANE  75,000  -", named="150,000  0", grand="170,000  10"
        ), 2025)
        self.assertEqual(len(rows), 2)
        self.assertEqual(validation["exactDuplicateSourceRows"], 1)
        self.assertEqual(validation["repeatedDisclosedNames"], [{"name": "SMITH,JANE", "rows": 2}])

    def test_printed_aggregate_rounding_is_recorded_without_changing_rows(self):
        rows, validation = IMPORTER.parse_layout(schedule(grand="95,001  10"), 2025)
        self.assertEqual(rows[0][3], 75000)
        self.assertEqual(validation["printedSubtotalRemunerationResidual"], -1)
        self.assertFalse(validation["printedSubtotalsReconcileExactly"])
        with self.assertRaises(ValueError):
            IMPORTER.parse_layout(schedule(grand="95,002  10"), 2025)

    def test_missing_rows_cannot_pass_the_locked_reviewed_totals(self):
        rows, validation = IMPORTER.parse_layout(schedule(), 2025)
        with self.assertRaises(ValueError):
            IMPORTER.validate_totals(rows, validation, ("hash", 1, 2, 150000, 0, 150000, 0))

    def test_coordinate_check_detects_a_changed_name_or_value(self):
        rows, _ = IMPORTER.parse_layout(schedule(), 2025)
        xml = b'''<html xmlns="http://www.w3.org/1999/xhtml"><body><page>
          <word xMin="10" xMax="60" yMin="10">EMPLOYEE</word>
          <word xMin="100" xMax="170" yMin="10">REMUNERATION</word>
          <word xMin="200" xMax="250" yMin="10">EXPENSES</word>
          <word xMin="10" xMax="70" yMin="30">SMITH,JANE</word>
          <word xMin="130" xMax="170" yMin="30">75,000</word>
          <word xMin="220" xMax="225" yMin="30">-</word>
        </page></body></html>'''
        self.assertEqual(IMPORTER.validate_coordinates(xml, rows, 1), 1)
        for changed in [xml.replace(b"SMITH,JANE", b"SMITH,JAN"), xml.replace(b"75,000", b"75,001")]:
            with self.assertRaises(ValueError):
                IMPORTER.validate_coordinates(changed, rows, 1)


if __name__ == "__main__":
    unittest.main()
