#!/usr/bin/env python3
"""Regression checks against retained original reader inputs, not a fresh crawl."""
import copy
import unittest

import recover_wave_municipal as r


class MunicipalRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=r.read(r.OUT/'sources.json')['sources']
        cls.by_id={s['id']:s for s in cls.sources}

    def test_all_native_fields_independently_replay(self):
        rows=[]
        for original in r.ORIGINALS:
            if original['method']=='native':
                evidence=r.read(r.OUT/'evidence'/f'{original["key"]}.json.gzip')
                rows += r.all_native_rows(evidence['readerInputs'],original)
        self.assertEqual(len(rows),80)
        self.assertEqual(sum(x['scope']==r.EMP for x in rows),63)
        self.assertEqual(sum(x['scope']==r.COUNCIL for x in rows),17)

    def test_independent_comparison_rejects_one_changed_cell(self):
        original=next(x for x in r.ORIGINALS if x['key']=='sooke-2025')
        inputs=copy.deepcopy(r.read(r.OUT/'evidence/sooke-2025.json.gzip')['readerInputs'])
        inputs['37']['layoutText']=inputs['37']['layoutText'].replace('157,929','157,930',1)
        with self.assertRaisesRegex(AssertionError,'Independent native reader mismatch'):
            r.all_native_rows(inputs,original)

    def test_wrapped_titles_off_baseline_expense_and_blank_cells(self):
        rows=r.read(r.OUT/'sooke-2025-employee-remuneration.json.gzip')
        lookup={row[1]:row for row in rows}
        self.assertEqual(lookup['Mills, Medea'][2:5],['Bylaw Enforcement Officer II/Business License Inspector',99970,33])
        self.assertEqual(lookup['Blewett, Duane'][2:5],['Manager of Subdivision Land Development - Approving Officer',134362,None])
        self.assertIsNone(lookup['Currie, Benjamin'][4])
        self.assertIsNone(lookup['Van Vianen, Nichole'][4])
        self.assertEqual(r.money('0'),0)
        self.assertIsNone(r.money('-'))
        self.assertIsNone(r.money(''))

    def test_manual_transcription_has_independent_peer_receipt(self):
        peer=r.verify_peer()
        self.assertTrue(peer['allRowFieldsExact'])
        rows=[]
        for source in self.sources:
            if source['employerSlug']=='village-of-mcbride':
                rows+=r.read(r.OUT/source['file'])
                self.assertEqual(source['validation']['independentPeerReview']['sha256'],r.PEER_SHA)
        self.assertEqual(len(rows),35)
        self.assertEqual(sum(row[2] is None for row in rows),10)

    def test_published_control_differences_are_not_adjusted(self):
        source=self.by_id['recovery-municipal-sooke-2025-employee-remuneration']
        self.assertEqual(source['totalRemuneration'],6874288)
        self.assertEqual(source['totalExpenses'],110428)
        self.assertEqual([c['residual'] for c in source['validation']['controls']],[1,-46])
        self.assertIn('172,064',source['publicWarning'])
        self.assertIn('cause unresolved',source['publicWarning'])
        source=self.by_id['recovery-municipal-mcbride-2022-elected-officials']
        self.assertEqual(source['totalRemuneration'],34965)
        self.assertEqual(source['totalExpenses'],24087.83)
        self.assertIn('55,812.83',source['publicWarning'])
        self.assertIn('unsigned',source['publicWarning'])

    def test_held_council_not_relabelled_or_imported(self):
        self.assertNotIn('recovery-municipal-mcbride-2025-elected-officials',self.by_id)
        source=self.by_id['recovery-municipal-mcbride-2025-employee-remuneration']
        self.assertTrue(source['completeEmployeeSchedule'])
        self.assertTrue(source['validation']['completeEmployeeSchedule'])
        self.assertEqual(source['pages'],[43])
        self.assertIn('2024',source['publicWarning'])
        self.assertEqual(len(self.sources),13)
        self.assertEqual(sum(s['rowCount'] for s in self.sources),115)


if __name__=='__main__':
    unittest.main()
