"""Offline checks for the new Lower Mainland municipal schedules and component holds."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import parse_wave_lower_mainland as parser


class MunicipalWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((parser.OUT/'reviewed-layouts.json').read_text())
        cls.sources = json.loads((parser.OUT/'sources.json').read_text())['sources']

    def source(self, slug, year, category='employee-remuneration'):
        return next(s for s in self.sources if s['employerSlug']==slug and s['year']==str(year) and s['category']==category)

    def rows(self, source):
        return json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))

    def evidence(self, source):
        return json.loads(gzip.decompress((parser.OUT/source['validation']['evidenceFile']).read_bytes()))

    def test_all_reader_fields_hashes_periods_counts_and_controls_reproduce(self):
        parser.build(self.config, parser.OUT, check_data=True)
        self.assertEqual(len(self.sources),23)
        self.assertEqual(sum(s['rowCount'] for s in self.sources),1069)
        self.assertEqual(sum(s['rowCount'] for s in self.sources if s['category']=='employee-remuneration'),1000)
        self.assertEqual(len({s['employerSlug'] for s in self.sources}),5)
        for s in self.sources:
            self.assertEqual(s['periodStart'],s['year']+'-01-01')
            self.assertEqual(s['periodEnd'],s['year']+'-12-31')

    def test_missing_benefits_are_held_even_when_known_cells_match_a_subtotal(self):
        counts=[]
        for year, expected in [(2023,11),(2024,2)]:
            s=self.source('city-of-abbotsford',year)
            self.assertEqual(s['validation']['heldMissingBenefitRows'],expected)
            self.assertIs(s['completeEmployeeSchedule'],False)
            self.assertIs(s['validation']['completeEmployeeSchedule'],False)
            imported={r[1] for r in self.rows(s)}
            held=s['validation']['heldRows']
            self.assertTrue(all(r['benefits'] is None and r['knownRemunerationColumn']>0 for r in held))
            self.assertTrue(all(r['name'] not in imported for r in held))
            self.assertIn('Partial employee cohort',s['publicWarning'])
            self.assertIn('scope',s['publicWarning'])
            counts.append(s['rowCount'])
        self.assertEqual(counts,[449,501])
        s=self.source('city-of-abbotsford',2023)
        self.assertNotIn('BEERS EDDY',{r[1] for r in self.rows(s)})
        self.assertEqual(next(r for r in s['validation']['heldRows'] if r['name']=='BEERS EDDY')['knownRemunerationColumn'],75171.36)

    def test_wrapped_title_stays_with_its_original_employee(self):
        rows={r[1]:r for r in self.rows(self.source('village-of-belcarra',2023))}
        self.assertEqual(rows['Novak, Stewart'][2],'Public Works and Emergency Preparedness Coordinator')
        self.assertEqual(rows['Richardson, Paula'][2],'Chief Administrative Officer')
        rows={r[1]:r for r in self.rows(self.source('village-of-harrison-hot-springs',2021))}
        self.assertEqual(rows['Key, Debra'][2],'Corporate Officer / Deputy Chief Administrative Officer')

    def test_blank_expenses_stay_missing_and_published_zero_stays_zero(self):
        rows=self.rows(self.source('village-of-belcarra',2013))
        self.assertTrue(all(r[4] is None for r in rows))
        rows={r[1]:r for r in self.rows(self.source('village-of-harrison-hot-springs',2021))}
        self.assertEqual(rows['Jones-Piron, Tracey'][4],0)
        for text in ['', '-', '–', '—', '‐']:
            self.assertIsNone(parser.money(text))
        self.assertEqual(parser.money('(252.96)'),-25296)
        self.assertEqual(parser.money('−252.96'),-25296)

    def test_expense_inclusive_totals_never_become_pay(self):
        s=self.source('city-of-abbotsford',2024,'elected-officials')
        row=next(r for r in self.rows(s) if r[1]=='BARKMAN LESTER')
        self.assertEqual(row[3:5],[59321,5673])
        proof=self.evidence(s)['componentRows'][0]
        self.assertEqual(proof['expenseInclusiveTotal'],6499300)
        self.assertEqual(proof['expenseInclusiveTotal']-proof['pay']-proof['expenses'],-100)
        self.assertIn('cause is unknown',s['publicWarning'])

    def test_missing_issuer_subtotals_are_explicit_not_claimed_reconciled(self):
        for s in self.sources:
            if s['employerSlug']!='village-of-harrison-hot-springs':continue
            self.assertTrue(s['validation']['namedControlUnavailable'])
            self.assertEqual(s['validation']['controls'],[])
            self.assertIn('subtotal',s['publicWarning'])
            self.assertEqual(s['validation']['heldMissingBenefitRows'],0)

    def test_only_printed_council_roles_are_imported(self):
        s=self.source('village-of-harrison-hot-springs',2022,'elected-officials')
        rows={r[1]:r for r in self.rows(s)}
        self.assertEqual(rows['Wood, Ed'][2],'Mayor')
        self.assertEqual(rows['Facio, Leo'][2],'Prior Mayor, current Councillor')
        self.assertIsNone(rows['Buckley, John'][2])

    def test_source_control_change_fails_without_rewriting_data(self):
        changed=copy.deepcopy(self.config)
        changed['reports'][0]['sections'][0]['controlsCents']['pay']+=100
        with self.assertRaisesRegex(ValueError,'changed residual'):
            parser.build(changed,parser.OUT,check_data=True)

    def test_changed_original_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            report=self.config['reports'][0]
            (Path(directory)/(report['key']+'.pdf')).write_bytes(b'%PDF-not-the-original')
            with self.assertRaisesRegex(ValueError,'fingerprint changed'):
                parser.build(self.config,Path(directory))

    def test_richmond_mayor_title_excludes_the_salary_currency_token(self):
        source=self.source('city-of-richmond',2024,'elected-officials')
        row=self.rows(source)[0]
        self.assertEqual(row[1:3],['Brodie, Malcolm','Mayor'])
        report=next(r for r in self.config['reports'] if r['employerSlug']=='city-of-richmond')
        section=copy.deepcopy(report['sections'][0])
        section['columns']['position'][1]=280
        section['columns']['salary'][0]=280
        with self.assertRaisesRegex(ValueError,'Currency token leaked'):
            parser.extract(self.evidence(source)['mupdfWords'],section)


if __name__=='__main__':
    unittest.main()
