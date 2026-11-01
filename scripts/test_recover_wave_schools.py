#!/usr/bin/env python3
"""Real-source regression checks for scan letters, literal controls, and scope."""
import copy
import gzip
import json
import unittest

import recover_wave_schools as s


class RecoverySchoolSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((s.COLLECTION/'sources.json').read_text())['sources']
        cls.proofs = {r['id']: json.loads(gzip.decompress((s.COLLECTION/r['provenanceFile']).read_bytes()))
                      for r in cls.sources}

    def test_offline_replay_all_rows_and_fingerprints(self):
        self.assertEqual(len(self.sources), 6)
        self.assertEqual(sum(r['rowCount'] for r in self.sources), 234)
        for source in self.sources:
            with self.subTest(source=source['id']):
                self.assertEqual(s.sha((s.COLLECTION/source['provenanceFile']).read_bytes()), source['provenanceSha256'])
                s.verify_source(source, self.proofs[source['id']])

    def test_scan_glyph_corrections_preserve_source_spelling_and_position(self):
        proof = self.proofs['recovery-schools-sd19-2025-employees']
        raw = {r['name'] for r in proof['rawMachineRows']}
        rows = {r['name']: r for r in proof['rows']}
        self.assertTrue({'lan Gardiner', 'Roberts Kubik', 'Gregory Kenyan'} <= raw)
        self.assertTrue({'Ian Gardiner', 'Roberta Kubik', 'Gregory Kenyon'} <= rows.keys())
        self.assertEqual(rows['Monica Penner']['position'], 'Speech language Patholoigist')
        self.assertIn('Jeremy WEddell', rows)
        trustees = self.proofs['recovery-schools-sd19-2025-trustees']['rows']
        self.assertEqual(trustees[1]['name'], 'Jodie Allen')

    def test_dashes_unknown_expense_are_distinct_from_explicit_zero(self):
        rows19 = self.proofs['recovery-schools-sd19-2025-employees']['rows']
        self.assertIsNone(next(r for r in rows19 if r['name'] == 'Adam Barraball')['expenses'])
        rows49 = self.proofs['recovery-schools-sd49-2025-trustees']['rows']
        self.assertEqual(next(r for r in rows49 if r['name'] == 'HOPPE, CHRISTINA')['expenses'], '0')
        self.assertTrue(all(r['position'] is None for r in rows49))

    def test_discrepant_controls_remain_literal_with_specific_public_warning(self):
        expected = {'recovery-schools-sd19-2025-employees': ['0', '2018'],
                    'recovery-schools-sd49-2025-trustees': ['-1', '0'],
                    'recovery-schools-sd64-2025-trustees': ['-2', '0.00']}
        for source in self.sources:
            with self.subTest(source=source['id']):
                if source['id'] in expected:
                    self.assertEqual(source['validation']['controlResiduals'], expected[source['id']])
                    self.assertFalse(source['validation']['summaryReconciles'])
                    self.assertIn('reason is unresolved', source['publicWarning'])
                else:
                    self.assertTrue(source['validation']['summaryReconciles'])
                    self.assertIsNone(source['publicWarning'])

    def test_native_reader_provenance_and_exact_employee_control(self):
        source = next(r for r in self.sources if r['id'] == 'recovery-schools-sd64-2025-employees')
        proof = self.proofs[source['id']]
        self.assertEqual(source['rowCount'], 110)
        self.assertEqual(source['validation']['computedComponentTotals'], ['12228711', '223125.00'])
        self.assertTrue(all('popplerSourceLine' in r for r in proof['rows']))
        self.assertTrue(all('mupdfWords' in r for r in proof['independentRows']))
        self.assertEqual(source['validation']['rowsByPhysicalPage'], {'52': 25, '53': 42, '54': 43})
        self.assertTrue(source['completeEmployeeSchedule'])

    def test_complete_scan_peer_review_and_native_employee_scope_are_distinct(self):
        manually_reviewed = [r for r in self.sources if 'independentNormalizedPayloadReview' in r['validation']]
        self.assertEqual(sum(r['rowCount'] for r in manually_reviewed), 124)
        self.assertEqual(len(manually_reviewed), 5)
        for source in self.sources:
            self.assertFalse(source['validation']['completeIndependentPeerImageReviewPending'])
        native_employees = next(r for r in self.sources if r['id'] == 'recovery-schools-sd64-2025-employees')
        self.assertNotIn('independentRenderedReview', native_employees['validation'])
        self.assertEqual(native_employees['validation']['independentReaders'],
                         ['Poppler lexical role delimiters', 'PyMuPDF geometric columns'])

    def test_mutated_field_cannot_pass_row_reader_comparison(self):
        source = self.sources[0]
        proof = copy.deepcopy(self.proofs[source['id']])
        proof['rows'][0]['expenses'] = None
        with self.assertRaises(AssertionError):
            s.verify_source(source, proof)

    def test_arrow_lakes_conflicting_period_remains_unaccepted(self):
        self.assertFalse(any(r['employerSlug'] == 'school-district-10' for r in self.sources))
        held = json.loads((s.RESEARCH/'held-originals.json').read_text())
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0]['inputKey'], 'sd10-2025')
        self.assertEqual(held[0]['periodConflict']['pdfPage'], 3)
        self.assertIn('June 30, 2024', held[0]['periodConflict']['literalDeclaration'])


if __name__ == '__main__':
    unittest.main()
