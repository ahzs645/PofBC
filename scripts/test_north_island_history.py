"""Regression checks for official NIC imports and fail-closed table parsing."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("import-north-island-history.py")
SPEC = importlib.util.spec_from_file_location("north_island_history", SCRIPT)
nic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nic)

FIXTURE = """NORTH ISLAND COLLEGE
SCHEDULE OF EMPLOYEE REMUNERATION AND EXPENSES
FIR SCHEDULE 1, SECTION 6
FOR THE YEAR ENDED MARCH 31, 2025
A. Board of Governors
    Board, Member    1,000    1
    1,000    1
B. Other Employees > $75,000
    Name    Remuneration    Expenses
    Employee, One    100,001    0
    100,001    0
C. Other Employees < $75,000
    Consolidated Remuneration / Expenses < $75,000    10    2
    TOTAL    101,011    3
    Page 1 of 1
\f"""


class FieldTests(unittest.TestCase):
    def test_source_dash_remains_missing_and_numeric_zero_is_zero(self):
        row, _ = nic.parse_employee("    Person, One    100,001    -", 6, "2024-25")
        zero, _ = nic.parse_employee("    Person, One    100,001    0", 6, "2024-25")
        self.assertIsNone(row[4])
        self.assertEqual(zero[4], 0)

    def test_newest_source_does_not_invent_a_position(self):
        row, _ = nic.parse_employee("    Person, One    100,001    -", 6, "2024-25")
        self.assertIsNone(row[2])
        with self.assertRaisesRegex(ValueError, "columns"):
            nic.parse_employee("    Person, One    Instructor    100,001    -", 6, "2024-25")

    def test_historical_position_column_is_required(self):
        with self.assertRaisesRegex(ValueError, "columns"):
            nic.parse_employee("    Person, One    100,001    -", 7, "2021-22")

    def test_reviewed_touching_columns_keep_every_letter(self):
        row, corrected = nic.parse_employee("    " + nic.ABUTTING + "    97,811    -", 10, "2022-23")
        self.assertTrue(corrected)
        self.assertEqual(row[1:3], [nic.SPLIT_NAME, nic.SPLIT_POSITION])
        with self.assertRaisesRegex(ValueError, "Unreviewed"):
            nic.parse_employee("    " + nic.ABUTTING + "    97,811    -", 10, "2018-19")

    def test_threshold_and_malformed_amounts_fail(self):
        for pay in ("75,000", "74,999", "100,00", "1O0,001"):
            with self.subTest(pay=pay), self.assertRaises(ValueError):
                nic.parse_employee(f"    Person, One    {pay}    -", 6, "2024-25")


class CompletenessTests(unittest.TestCase):
    def setUp(self):
        reviewed = copy.deepcopy(nic.REVIEWED["2024-25"])
        reviewed.update({"pdfPages": 1, "pages": [1], "pageCounts": [1],
                         "sums": [100001, 0], "controls": [100001, 0],
                         "board": [1000, 1], "below": [10, 2], "grand": [101011, 3]})
        self.context = patch.dict(nic.REVIEWED, {"2024-25": reviewed})
        self.context.start()
        self.addCleanup(self.context.stop)

    def test_only_named_employees_become_rows(self):
        rows, validation = nic.parse_layout(FIXTURE, "2024-25")
        self.assertEqual(rows, [[nic.EMPLOYER, "Employee, One", None, 100001, 0, 1]])
        self.assertTrue(validation["summaryTotalReconciled"])

    def test_wrong_period_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "reporting period"):
            nic.parse_layout(FIXTURE.replace("MARCH 31, 2025", "MARCH 31, 2024"), "2024-25")

    def test_omitted_employee_cannot_pass_using_unchanged_totals(self):
        text = FIXTURE.replace("    Employee, One    100,001    0\n", "")
        with self.assertRaisesRegex(ValueError, "employee section"):
            nic.parse_layout(text, "2024-25")

    def test_changed_money_or_unparsed_row_cannot_be_silently_dropped(self):
        for changed in (FIXTURE.replace("Employee, One    100,001", "Employee, One    100,002"),
                        FIXTURE.replace("    100,001    0\nC.", "    unreadable employee payment\n    100,001    0\nC.")):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                nic.parse_layout(changed, "2024-25")

    def test_missing_terminal_page_boundary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "page boundaries"):
            nic.parse_layout(FIXTURE.rstrip("\f"), "2024-25")


class AcceptedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = SCRIPT.parents[1] / "research/salaries/north-island-history"
        cls.manifest = json.loads((cls.directory / "sources.json").read_text())

    def test_all_five_cohorts_match_hashes_and_controls(self):
        self.assertEqual(len(self.manifest["sources"]), 4)
        self.assertEqual(sum(s["rowCount"] for s in self.manifest["sources"]), 608)
        total = 0
        for source in self.manifest["sources"] + self.manifest["verificationOnlySources"]:
            with self.subTest(period=source["year"]):
                data = (self.directory / source["file"]).read_bytes()
                raw = gzip.decompress(data)
                self.assertEqual(nic.sha256(data), source["dataSha256"])
                self.assertEqual(nic.sha256(raw), source["normalizedSha256"])
                rows = json.loads(raw)
                self.assertEqual(len(rows), source["rowCount"])
                self.assertTrue(all(len(r) == 6 and r[0] == nic.EMPLOYER and r[3] > 75000 and r[5] in source["pages"] for r in rows))
                self.assertEqual(sum(r[3] for r in rows), source["totalRemuneration"])
                self.assertEqual(sum(r[4] for r in rows if r[4] is not None), source["totalExpenses"])
                self.assertTrue(source["validation"]["allNamesTitlesAndMonetaryCellsIndependentlyVerified"])
                if source["year"] == "2024/25":
                    self.assertTrue(all(r[2] is None for r in rows))
                total += len(rows)
        self.assertEqual(total, 808)

    def test_existing_2024_cohort_is_verified_once_and_not_reimported(self):
        source, = self.manifest["verificationOnlySources"]
        rows = json.loads(gzip.decompress((self.directory / source["file"]).read_bytes()))
        self.assertEqual(nic.existing_publication(rows, source), source)
        changed = copy.deepcopy(rows)
        changed[0][4] = 0 if changed[0][4] is None else changed[0][4] + 1
        with self.assertRaisesRegex(ValueError, "cohort differs"):
            nic.existing_publication(changed, source)

    def test_source_disagreement_is_disclosed_not_adjusted(self):
        source = next(s for s in self.manifest["sources"] if s["year"] == "2018/19")
        validation = source["validation"]
        self.assertFalse(validation["summaryTotalReconciled"])
        self.assertEqual((validation["remunerationResidual"], validation["expensesResidual"]), (-10, 5))
        self.assertIsNone(validation["residualCause"])
        self.assertIn("cause is unconfirmed", source["publicWarning"])
        self.assertEqual(source["totalRemuneration"], 12415381)

    def test_compiled_overlap_records_two_name_title_errors(self):
        review = json.loads((self.directory / "compiled-period-comparison.json").read_text())
        self.assertEqual(review["compiledRows"], 181)
        self.assertEqual(review["officialRows"], 181)
        self.assertEqual(review["exactNormalizedNamePayExpenseMatches"], 179)
        self.assertEqual({r["compiledName"] for r in review["unmatchedCompiledNameRows"]},
                         {"Lawrence, Jeffrey Instructor", "Lowey Mackenzie, Kerri Inst"})
        self.assertTrue(review["paymentMultisetMatches"])

    def test_scanned_2019_report_is_a_lead_and_not_an_import(self):
        leads = self.manifest["unparsedSources"]
        self.assertEqual(len(leads), 1)
        lead = leads[0]
        self.assertEqual((lead["year"], lead["status"]), ("2019/20", "requires-ocr"))
        self.assertNotIn("file", lead)
        self.assertEqual(lead["sourceUrl"], nic.BASE_URL + "2019-20.pdf")
        self.assertEqual(lead["discoveryEvidence"]["renderedCoverFiscalYearEnd"], "2020-03-31")
        self.assertFalse(lead["discoveryEvidence"]["employeeScheduleAccepted"])
        self.assertEqual(lead["discoveryEvidence"]["observedTargetUrl"], lead["sourceUrl"])
        self.assertEqual(len(lead["discoveryEvidence"]["indexLabels"]), 2)
        self.assertTrue(all(s["year"] != "2019/20" for s in self.manifest["sources"]))


if __name__ == "__main__":
    unittest.main()
