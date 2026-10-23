"""Regression checks for source-format risks found in the official CSV series."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("public_accounts", Path(__file__).with_name("import-public-accounts.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicAccountsSources(unittest.TestCase):
    def test_csv_year_conflict_stops_import(self):
        data = b'"Salary for the Fiscal Year Ended March 31, 2020",,\r\nName,Position Title,Amount\r\n"Lee,Jess",Analyst,85000\r\n'
        with self.assertRaisesRegex(ValueError, "heading says"):
            module.parse_table(data, "employees", 2021)

    def test_published_rounded_column_and_summary_are_not_extra_people(self):
        data = b'Name,Position Title,Rounded\r\n"Lee,Jess",Analyst,"85,000.00"\r\n,,"85,000.00"\r\n'
        rows, validation = module.parse_table(data, "employees", 2010)
        self.assertEqual(rows, [["public-service", "Lee,Jess", "Analyst", 85000, None]])
        self.assertTrue(validation["summaryTotalReconciled"])
        with self.assertRaisesRegex(ValueError, "total does not reconcile"):
            module.parse_table(data.replace(b',,"85,000.00"', b',,"86,000.00"'), "employees", 2010)

    def test_legacy_cp1252_is_decoded_without_destroying_names(self):
        data = 'Name,Position Title,Amount\r\n"Wenezenki–Yolland,Cheryl",Deputy,85000\r\n'.encode("cp1252")
        rows, validation = module.parse_table(data, "employees", 2018)
        self.assertEqual(rows[0][1], "Wenezenki–Yolland,Cheryl")
        self.assertEqual(validation["encoding"], "cp1252")

    def test_nil_oic_rows_are_not_zero_salary_and_recovery_is_retained(self):
        data = 'NAME,TITLE,AMOUNT\r\n"Lee,Jess",Deputy,-\r\n"Liu,Susan",Coordinator,–5110\r\n'.encode("cp1252")
        rows, validation = module.parse_table(data, "appointees", 2023)
        self.assertEqual(rows, [["public-service", "Liu,Susan", "Coordinator", -5110, None]])
        self.assertEqual(validation["excludedNilPayRows"], 1)
        self.assertEqual(validation["negativeRemunerationRows"], 1)

    def test_2008_uses_published_amount_not_internal_adjustment_column(self):
        data = b'Name,Amount,Amount,Other,Total ADJ\r\n"Lee,Jess","84,266","84,265.63",,0\r\n'
        rows, _ = module.parse_table(data, "employees", 2008)
        self.assertEqual(rows, [["public-service", "Lee,Jess", None, 84266, None]])

    def test_travel_matching_does_not_expand_initials(self):
        self.assertEqual(module.name_key("Lee, Charlotte"), module.name_key("LEE,CHARLOTTE"))
        self.assertNotEqual(module.name_key("Lee,C"), module.name_key("Lee,Charlotte"))
        data = b'Name,Amount\r\n"LEE,CHARLOTTE",7000\r\n"Lee, Charlotte",8000\r\n'
        names, validation = module.parse_travel(data, 2024)
        self.assertEqual(len(names[module.name_key("Lee,Charlotte")]), 2)
        self.assertEqual(validation["ambiguousNames"], 1)

    def test_travel_matching_preserves_surname_given_boundary(self):
        self.assertNotEqual(module.name_key("Li,Anne"), module.name_key("Lian,Ne"))

    def test_travel_year_conflict_stops_import(self):
        data = b'"Travel for the Fiscal Year Ended March 31, 2020",\r\nName,Amount\r\n"Lee,Jess",8500\r\n'
        with self.assertRaisesRegex(ValueError, "heading says"):
            module.parse_travel(data, 2021)


if __name__ == "__main__":
    unittest.main()
