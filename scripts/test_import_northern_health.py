"""Regressions for actual layout and omission risks in the Northern Health PDFs."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("northern_health", Path(__file__).with_name("import-northern-health-salaries.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NorthernHealthSources(unittest.TestCase):
    def test_separated_accounting_minus_cannot_shift_expense_into_salary(self):
        row = module.parse_row("Buvyer,Sophia                    114,088 -         630", 7)
        self.assertEqual(row, ["northern-health", "Buvyer,Sophia", None, 114088, -630, 7])

    def test_parentheses_zero_and_missing_expenses_are_distinct(self):
        self.assertEqual(module.amount("(726)"), -726)
        self.assertEqual(module.amount("- 0"), 0)
        self.assertIsNone(module.amount("-"))
        self.assertIsNone(module.amount(""))
        with self.assertRaisesRegex(ValueError, "monetary token"):
            module.amount("- 630 532")

    def test_missing_employee_fails_reviewed_row_and_total_gate(self):
        rows = [["northern-health", "Lee, Jess", None, 100000, 5, 1],
                ["northern-health", "Lin, Sam", None, 100001, None, 1]]
        validation = {"physicalPdfPages": [1, 1], "printedNamedRemuneration": 200001,
                      "printedNamedExpenses": 5, "exactDuplicateSourceRows": 0}
        reviewed = ("unused", 1, 2, 200001, 5, 200001, 5)
        module.verify_reviewed_totals(rows, dict(validation), reviewed)
        with self.assertRaisesRegex(ValueError, "Reviewed rows"):
            module.verify_reviewed_totals(rows[:1], dict(validation), reviewed)

    def test_source_year_conflict_stops_import(self):
        with self.assertRaisesRegex(ValueError, "fiscal period"):
            module.parse_layout("FOR THE FISCAL YEAR ENDED MARCH 31, 2021\n", 2022)

    def test_under_threshold_aggregate_is_not_an_employee(self):
        text = ("FOR THE FISCAL YEAR ENDED MARCH 31, 2021\n"
                "Employee        REMUNERATION        EXPENSES\n"
                "Lee, Jess        100,000             5\n"
                "TOTAL EMPLOYEES > $75,000    $ 100,000 $ 5\n"
                "TOTAL EMPLOYEES = OR < $75,000   $ 300,000 $ 8\n"
                "GRAND TOTAL  $ 400,000 $ 13\n\f")
        rows, validation = module.parse_layout(text, 2021)
        self.assertEqual(len(rows), 1)
        self.assertEqual(validation["underThresholdRemunerationExcluded"], 300000)
        with self.assertRaisesRegex(ValueError, "Unparsed employee line"):
            module.parse_layout(text.replace("Lee, Jess", "Unknown row\nLee, Jess"), 2021)


if __name__ == "__main__":
    unittest.main()
