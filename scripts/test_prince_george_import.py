import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('pg',Path(__file__).with_name('import-prince-george-salaries.py'))
pg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


class PrinceGeorgeImportTests(unittest.TestCase):
    def test_printed_total_is_not_added_to_its_components(self):
        self.assertEqual(pg.amount_from_components([8000000,500000,200000,None,8700000,12345],2021),(8700000,12345))

    def test_new_format_includes_other_compensation_above_threshold(self):
        self.assertEqual(pg.amount_from_components([7400000,200000,5000],2025),(7600000,5000))

    def test_inconsistent_old_total_fails(self):
        with self.assertRaises(ValueError):pg.amount_from_components([8000000,None,None,None,8000001,None],2021)

    def test_new_format_does_not_pass_base_pay_alone_at_threshold(self):
        with self.assertRaises(ValueError):pg.amount_from_components([7500000,None,5000],2025)

    def test_missing_zero_and_negative_expenses_are_distinct(self):
        self.assertIsNone(pg.cents('-'))
        self.assertEqual(pg.cents('0.00'),0)
        self.assertEqual(pg.cents('(104.33)'),-10433)

    def test_elected_total_excludes_expense_and_benefit_columns(self):
        self.assertEqual(pg.amount_from_components([14000000,900000,14900000,125000,20000],2025,True),(14900000,125000))

    def test_multiset_comparison_preserves_duplicate_rows(self):
        row=['Smith, A','Clerk',8000000,None,3,[8000000,None,None]]
        with self.assertRaises(ValueError):pg.compare_readers([row,row],[row])

    def test_glyph_identity_preserves_comma_and_restores_hyphen(self):
        class Page:
            def get_texttrace(self):
                raw='A,B, C'
                return [{'font':'FranklinGothicBook','chars':[(ord(c),16 if i==1 else 15 if c==',' else 1,None,None) for i,c in enumerate(raw)]}]
        name,position,changes=pg.glyph_corrected_fields(Page(),'A,B, C','Manager')
        self.assertEqual(name,'A-B, C')
        self.assertEqual(position,'Manager')
        self.assertEqual(len(changes),1)


if __name__=='__main__':unittest.main()
