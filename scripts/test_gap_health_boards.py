"""Actual-source board regressions and adversarial semantic mutations."""
import copy
import gzip
import json
from pathlib import Path
import unittest

import gap_health_boards as g


class BoardHistories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs={s['id']:s for s in json.loads((g.AREA/'source-specs.json').read_bytes())}
        cls.proofs={k:json.loads(gzip.decompress((g.OUT/'evidence'/(k+'.json.gzip')).read_bytes())) for k in cls.specs}

    def rows(self,identifier):
        return g.compare_native_rows(self.proofs[identifier],self.specs[identifier])[0]

    def test_all_twenty_five_actual_reports_compare_every_named_row(self):
        named=numeric=held=0
        for identifier,spec in self.specs.items():
            rows=self.rows(identifier)
            self.assertEqual(len(rows),spec['namedRows'])
            named+=len(rows);numeric+=sum(r[3] is not None for r in rows);held+=sum(r[3] is None for r in rows)
        self.assertEqual((len(self.specs),named,numeric,held),(25,323,266,57))

    def test_actual_period_headers_and_twenty_six_control_cells_match_both_readers(self):
        controls=0
        for identifier,spec in self.specs.items():
            got=g.validate_source_readings(self.proofs[identifier],spec)
            self.assertEqual(got['pymupdf'],got['poppler'])
            controls+=len(got['pymupdf'])
        self.assertEqual(controls,26)

    def test_expense_inclusive_island_total_never_becomes_remuneration(self):
        rows=self.rows('gap-health-boards-island-2025-26')
        self.assertEqual(rows[0],['island-health','Andrew Adams','Director',29065,8597,1])
        self.assertEqual(rows[3][3:5],[32370,None])
        self.assertNotEqual(rows[0][3],37662)

    def test_source_name_variants_survive_across_periods(self):
        newer=self.rows('gap-health-boards-island-2025-26');older=self.rows('gap-health-boards-island-2024-25')
        self.assertEqual(newer[0][1],'Andrew Adams');self.assertEqual(older[0][1],'Andy Adams')
        self.assertEqual(newer[4][1],'Anne Davies');self.assertEqual(older[4][1],'Anne Davis')

    def test_expense_inclusive_zero_does_not_convert_dash_pay_components_to_zero(self):
        rows=self.rows('gap-health-boards-island-2023-24')
        row=next(r for r in rows if r[1]=='Harold Cull')
        self.assertIsNone(row[3]);self.assertIsNone(row[4])
        _,evidence,_,_=g.compare_native_rows(self.proofs['gap-health-boards-island-2023-24'],self.specs['gap-health-boards-island-2023-24'])
        self.assertEqual(next(e for e in evidence if e['row'][1]=='Harold Cull')['printedRowTotal'],0)

    def test_recovered_island_nonnumeric_pay_keeps_known_expenses_separate(self):
        rows=self.rows('gap-health-boards-island-2018-19')
        row=next(r for r in rows if r[1]=='Diane Brennan')
        self.assertEqual(row[3:5],[None,657])
        self.assertEqual(sum(r[4] or 0 for r in rows),41378)

    def test_providence_dash_only_years_have_no_salary_observations(self):
        for year,n,expenses in [('2020-21',18,231),('2021-22',20,1372)]:
            rows=self.rows('gap-health-boards-providence-'+year)
            self.assertEqual(len(rows),n);self.assertTrue(all(r[3] is None for r in rows))
            self.assertEqual(sum(r[4] or 0 for r in rows),expenses)
        row=next(r for r in self.rows('gap-health-boards-providence-2021-22') if 'Keil' in r[1])
        self.assertEqual(row[1],'Keility, Karen')

    def test_providence_numeric_subsets_reconcile_with_excluded_expense_rows(self):
        for year,n,pay,known,held,full in [('2022-23',10,96500,1987,1157,3144),('2024-25',9,100000,4046,2404,6450)]:
            rows=self.rows('gap-health-boards-providence-'+year)
            imported=[r for r in rows if r[3] is not None];excluded=[r for r in rows if r[3] is None]
            self.assertEqual((len(imported),sum(r[3] for r in imported),sum(r[4] or 0 for r in imported)),(n,pay,known))
            self.assertEqual(sum(r[4] or 0 for r in excluded),held);self.assertEqual(known+held,full)

    def test_vch_retainer_and_meeting_fees_exclude_reimbursements(self):
        rows=self.rows('gap-health-boards-vch-2022-23')
        self.assertEqual(rows[0],['vancouver-coastal-health','Au, Wendy','Member',15250,130,2])
        self.assertEqual((len(rows),sum(r[3] for r in rows),sum(r[4] or 0 for r in rows)),(11,212625,5452))
        self.assertEqual(next(r for r in rows if r[1]=='McLaughlin, John')[3],12375)

    def test_literal_phsa_subtotal_residuals_are_not_adjusted(self):
        rows=self.rows('gap-health-boards-phsa-2020-21')
        self.assertEqual((sum(r[3] for r in rows),sum(r[4] or 0 for r in rows)),(215875,2718))
        self.assertEqual(sum(r[3]+(r[4] or 0) for r in rows)-218595,-2)
        earlier=self.rows('gap-health-boards-phsa-2015-16')
        self.assertIsNone(next(r for r in earlier if r[1]=='Wynne Powell')[3])

    def test_changed_independent_monetary_reader_fails_closed(self):
        identifier='gap-health-boards-island-2025-26';proof=copy.deepcopy(self.proofs[identifier]);spec=self.specs[identifier]
        targets=[w for w in proof['poppler'][0] if w[4]=='14,400' and 90<(w[1]+w[3])/2<115]
        self.assertEqual(len(targets),1);targets[0][4]='14,401'
        with self.assertRaisesRegex(ValueError,'independent reader disagreement'):g.compare_native_rows(proof,spec)

    def test_changed_printed_control_is_rejected_even_with_unchanged_rows(self):
        identifier='gap-health-boards-island-2025-26';proof=copy.deepcopy(self.proofs[identifier]);spec=self.specs[identifier]
        targets=[w for w in proof['poppler'][0] if w[4]=='290,027'];self.assertEqual(len(targets),1);targets[0][4]='290,028'
        with self.assertRaises(AssertionError):g.validate_source_readings(proof,spec)

    def test_changed_internal_header_period_is_rejected(self):
        identifier='gap-health-boards-island-2025-26';proof=copy.deepcopy(self.proofs[identifier]);spec=self.specs[identifier]
        words=proof['poppler'][0];targets=[w for w in words if '2026' in w[4] and (w[1]+w[3])/2<90]
        self.assertEqual(len(targets),1);targets[0][4]=targets[0][4].replace('2026','2027')
        with self.assertRaises(AssertionError):g.validate_source_readings(proof,spec)

    def test_absent_source_expense_columns_remain_unknown(self):
        for identifier in ['gap-health-boards-phsa-2015-16','gap-health-boards-phsa-2016-17','gap-health-boards-phsa-2017-18','gap-health-boards-island-2015-16','gap-health-boards-island-2016-17','gap-health-boards-island-2017-18']:
            self.assertTrue(all(r[4] is None for r in self.rows(identifier)))

    def test_reviewed_source_pin_rejects_a_later_pdf_with_identical_rows(self):
        identifier='gap-health-boards-vch-2022-23';spec=self.specs[identifier]
        data=g.sha((g.OUT/(identifier+'.json.gzip')).read_bytes())
        review={'pins':{identifier:{'sourceId':identifier,'sourceSha256':spec['sha256'],'dataSha256':data}}}
        g.validate_review_source(review,identifier,spec['sha256'],data)
        with self.assertRaisesRegex(AssertionError,'reviewed source changed'):
            g.validate_review_source(review,identifier,'0'*64,data)

    def test_reviewed_row_pin_rejects_edited_rows_or_an_unreviewed_scope(self):
        identifier='gap-health-boards-providence-2024-25';spec=self.specs[identifier]
        data=g.sha((g.OUT/(identifier+'.json.gzip')).read_bytes())
        review={'pins':{identifier:{'sourceId':identifier,'sourceSha256':spec['sha256'],'dataSha256':data}}}
        with self.assertRaisesRegex(AssertionError,'reviewed rows changed'):
            g.validate_review_source(review,identifier,spec['sha256'],'0'*64)
        with self.assertRaises(KeyError):
            g.validate_review_source(review,'unreviewed-year',spec['sha256'],data)

if __name__=='__main__':unittest.main()
