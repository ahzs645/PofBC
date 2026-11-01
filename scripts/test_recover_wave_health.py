#!/usr/bin/env python3
"""Regression checks for real wrapped names, source footnotes and held OCR."""
import gzip
import json
import unittest

import recover_wave_health as recovery
import recover_wave_health_employee_staging as staging


class HistoricalHealthRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {s['year']:s for s in json.loads((recovery.OUT/'source-specs.json').read_text())}

    def evidence(self, year):
        spec = self.specs[year]
        return json.loads(gzip.decompress((recovery.OUT/'evidence'/(spec['id']+'.json.gzip')).read_bytes()))

    def test_complete_offline_replay(self):
        recovery.run(check=True)
        staging.run(check=True)

    def test_wrapped_names_titles_and_per_diem_components(self):
        rows, a, b = recovery.parse_and_compare(self.evidence('2016/17'), self.specs['2016/17'])
        self.assertEqual(rows[6][1:4], ['Findlay (Frank) Quinn', 'Director (Apr 2016 - Dec 2016)', 9125])
        self.assertEqual(rows[7][1], 'Dennis Rounsville')
        self.assertEqual(rows[8][1:3], ['Tammy Tugnum', 'Director'])
        self.assertEqual(a[3]['components'][-1], 625)
        self.assertTrue(all(r[4] is None for r in rows))

    def test_source_explicit_zero_and_superscript_not_payment(self):
        rows, _, _ = recovery.parse_and_compare(self.evidence('2014/15'), self.specs['2014/15'])
        self.assertEqual(rows[3], ['interior-health','Debra Cannon','Director',0,None,2])
        self.assertEqual(rows[5][3], 21594)
        self.assertEqual(sum(r[3] for r in rows),160689)

    def test_independent_reader_rejects_single_amount_mutation(self):
        changed = self.evidence('2017/18')
        changed['popplerLayoutText'] = changed['popplerLayoutText'].replace('$3,500', '$3,501', 1)
        with self.assertRaisesRegex(ValueError,'independent field disagreement'):
            recovery.parse_and_compare(changed,self.specs['2017/18'])

    def test_literal_published_control_difference(self):
        manifest = json.loads((recovery.OUT/'sources.json').read_text())
        source = next(s for s in manifest['sources'] if s['year']=='2017/18')
        self.assertEqual(source['totalRemuneration'],169627)
        self.assertEqual(source['validation']['printedRemunerationTotal'],169625)
        self.assertEqual(source['validation']['remunerationControlResidual'],2)
        self.assertIn('2 CAD',source['publicWarning'])

    def test_ocr_failure_is_staged_and_nulls_preserved(self):
        e = json.loads(gzip.decompress((staging.OUT/'phsa-2024-25-page-1-staged.json.gzip').read_bytes()))
        abia = next(r for r in e['rowEvidence'] if r['visibleName']=='Abia,Jo-Ann')
        self.assertEqual(abia['rawTesseractExpense'],'™m')
        self.assertEqual(abia['visibleExpense'],771)
        self.assertEqual(e['acceptedRows'],0)
        self.assertFalse(e['completeEmployeeSchedule'])
        self.assertEqual(e['physicalPagesNotReviewed']['count'],283)
        self.assertEqual(sum(r[4] is None for r in e['rows']),18)
        self.assertEqual(e['rows'][3][1],'Abadi,Shirin')


if __name__ == '__main__':
    unittest.main()
