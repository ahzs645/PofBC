#!/usr/bin/env python3
"""Regression checks for actual shared OCR and source-scope failures."""
import gzip
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COLLECTION=ROOT/'research/salaries/queue-completion-municipal'
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
def load(path):return json.loads(gzip.decompress(path.read_bytes())) if path.suffix=='.gzip' else json.loads(path.read_text())

class SourceRegressions(unittest.TestCase):
    def test_shared_ocr_error_does_not_override_literal_one(self):
        old=COLLECTION/'mission-2023-employee-remuneration.json.gzip'
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),'24ac7b07cf0c1f7e3e391dffb52d0de98c66b129a758ae1fb180dfa613ba504b')
        prior=load(old);final=load(COLLECTION/'mission-2023-employee-remuneration-v2.json.gzip')
        self.assertEqual(prior[10][3],93274)
        self.assertEqual(final[10],['city-of-mission','Blaschuk, S','Building Inspector 2',93271,1718,6])
        self.assertEqual([(i,j) for i in range(148) for j in range(6) if prior[i][j]!=final[i][j]],[(10,3)])
        context=load(AREA/'mission-2023-context-review-v2.json')
        self.assertEqual(context['literalControlDiscrepancies']['specificRow']['printedExpenseInclusiveTotal'],94992)
        self.assertEqual(sum(r[3] for r in final),16445762)
        self.assertEqual(context['literalControlDiscrepancies']['namedRowSumMinusPrinted']['remuneration'],-3)

    def test_merged_council_columns_are_source_separated(self):
        rows=load(COLLECTION/'vernon-2025-elected-officials.json.gzip')
        self.assertEqual(rows[0][1:3],['Cumming, Victor','Mayor'])
        self.assertEqual(rows[-1][1:3],['Quiring, Brian F','Councillor'])
        self.assertTrue(all(r[2]=='Councillor' for r in rows[1:]))
        self.assertTrue(all('Councillor' not in r[1] and 'Mayor' not in r[1] for r in rows))

    def test_actual_zero_and_dash_remain_distinct(self):
        mission=load(COLLECTION/'mission-2025-employee-remuneration.json.gzip')
        vernon=load(COLLECTION/'vernon-2025-employee-remuneration.json.gzip')
        self.assertIsNone(next(r for r in mission if r[1]=='Baah, B')[4])
        self.assertEqual(next(r for r in vernon if r[1]=='Becraft, S')[4],0)
        self.assertEqual(sum(r[4] is None for r in mission),31)
        self.assertEqual(sum(r[4]==0 for r in vernon),25)
        self.assertTrue(all(r[2] is None for r in vernon))

    def test_source_combined_selection_is_not_pay_only(self):
        source=load(AREA/'mission-2023-employee-remuneration-source-spec.json')
        rows=load(COLLECTION/source['file'])
        self.assertIsNone(source['threshold'])
        self.assertIn('remuneration and expenses',source['publishedSelectionCriterion'])
        self.assertTrue(any(r[3]<75000 and r[3]+(r[4] or 0)>75000 for r in rows))

    def test_final_manifest_has_all_retention_guards_and_no_held_duplicates(self):
        sources=load(COLLECTION/'sources.json')['sources']
        self.assertEqual(len(sources),9)
        self.assertEqual(sum(s['rowCount'] for s in sources),835)
        self.assertNotIn('mission-2023-employee-remuneration.json.gzip',[s['file'] for s in sources])
        self.assertFalse(any(s['employerSlug']=='village-of-mcbride' for s in sources))
        self.assertFalse(any(s['employerSlug']=='town-of-creston' and s['category']=='elected-officials' for s in sources))
        for source in sources:
            self.assertTrue(source['retainCompiledPartition'])
            self.assertTrue(source['publicWarning'])
            self.assertTrue(source['validation']['compiledPartitionRetained'])
            self.assertTrue(source['validation']['compiledPartitionRetentionReason'])
            self.assertEqual(source['completeEmployeeSchedule'],source['validation']['completeEmployeeSchedule'])

    def test_actual_pdf_painted_inputs_reproduced(self):
        receipt=load(AREA/'original-replay-verification.json')
        self.assertEqual(len(receipt['originalPdfPaintedRenderRechecks']),30)
        self.assertTrue(all(r['matchesFrozenRawOcrInput'] for r in receipt['originalPdfPaintedRenderRechecks']))

if __name__=='__main__':unittest.main()
