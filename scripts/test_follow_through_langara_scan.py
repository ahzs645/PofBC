#!/usr/bin/env python3
"""Self-contained checks of the accepted Langara FY2024 scan and OCR receipts."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import follow_through_langara_scan as parser


class LangaraScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=json.loads(gzip.decompress((parser.OUT/'evidence/langara-2023-24.json.gzip').read_bytes()))
        cls.source=next(s for s in json.loads((parser.OUT/'sources.json').read_text())['sources'] if s['id']==parser.SOURCE_ID)
        cls.data=(parser.OUT/cls.source['file']).read_bytes()
        cls.rows=json.loads(gzip.decompress(cls.data))

    def test_complete_census_and_literal_controls(self):
        self.assertEqual(len(self.rows),891)
        self.assertEqual(parser.Counter(r[5] for r in self.rows),parser.Counter({**{p:86 for p in range(32,42)},42:31}))
        self.assertEqual([sum(r[i] or 0 for r in self.rows) for i in [3,4]],[94671610,2754209])
        self.assertEqual([c['printedControl'] for c in self.source['validation']['printedControls']],[94671616,2754193])
        self.assertEqual([c['residual'] for c in self.source['validation']['printedControls']],[-6,16])
        self.assertEqual(self.evidence['controlReconciliation']['allPrintedFinancialReconciliationResiduals'],0)

    def test_both_raw_ocr_passes_reproduce_complete_source_rows(self):
        for number,raw in enumerate(self.evidence['rawOcrPasses'],1):
            parsed=[]
            self.assertEqual(raw['OMP_THREAD_LIMIT'],1)
            self.assertEqual(raw['OMP_NUM_THREADS'],1)
            for page in raw['pages']:
                self.assertEqual(hashlib.sha256(page['tsv'].encode()).hexdigest(),page['tsvSha256'])
                parsed+=parser.parse(parser.words_from_tsv(page['tsv'],raw['renderScale']),page['pdfPage'])
            self.assertEqual(parsed,self.evidence[f'ocrPass{number}Rows'])
        resolved,corrections=parser.resolved_rows(self.evidence['ocrPass1Rows'],self.evidence['ocrPass2Rows'])
        self.assertEqual(resolved,self.rows)
        self.assertEqual(corrections,self.evidence['textCorrectionsFromSourcePixels'])
        self.assertEqual(len(corrections),21)

    def test_all_money_cells_agree_and_missing_is_not_zero(self):
        for a,b in zip(self.evidence['ocrPass1Rows'],self.evidence['ocrPass2Rows']):
            self.assertEqual(a['amounts'],b['amounts'])
        self.assertEqual(sum(r[4] is None for r in self.rows),19)
        self.assertEqual(sum(r[4]==0 for r in self.rows),0)
        self.assertEqual(parser.money('0'),0)
        self.assertIsNone(parser.money('-'))
        self.assertEqual(parser.money('(8)'),-8)

    def test_shared_ocr_surname_error_is_corrected_from_source_pixels(self):
        self.assertEqual(self.evidence['ocrPass1Rows'][879]['cells'][0],'Zanzerl|, Heather')
        self.assertEqual(self.evidence['ocrPass2Rows'][879]['cells'][0],'Zanzerl|, Heather')
        self.assertEqual(self.rows[879][1],'Zanzerl, Heather')
        self.assertEqual(self.rows[766][1],'Todd Stuckless, J.')
        self.assertEqual(self.rows[490][1],'Mardukhi, Jian')

    def test_named_below_threshold_rows_and_duplicate_names_are_retained(self):
        self.assertEqual(sum(r[3]<=75000 for r in self.rows),31)
        self.assertEqual(min(r[3] for r in self.rows),64147)
        wong=[r for r in self.rows if r[1]=='Wong, Kenneth']
        self.assertEqual(len(wong),2)
        self.assertEqual([r[3] for r in wong],[115575,128115])
        self.assertFalse(any(r[1].startswith(('Total','Schedule','Salary')) for r in self.rows))

    def test_data_hashes_and_determinism(self):
        raw=gzip.decompress(self.data)
        self.assertEqual(hashlib.sha256(self.data).hexdigest(),self.source['dataSha256'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),self.source['normalizedSha256'])
        self.assertEqual(gzip.compress(raw,mtime=0),self.data)
        self.assertEqual(self.source['periodStart'],'2023-04-01')
        self.assertEqual(self.source['periodEnd'],'2024-03-31')

    def test_complete_cell_review_receipts_and_accepted_disposition(self):
        visual=json.loads((parser.OUT/'visual/langara-2023-24.json').read_text())
        self.assertEqual(visual['reviewedPhysicalPages'],parser.PAGES)
        self.assertEqual(visual['employeeRowsReviewed'],891)
        self.assertEqual(len(visual['completeCellReviewImages']),22)
        for p in visual['completeCellReviewImages']:
            self.assertEqual(hashlib.sha256((parser.OUT/p['file']).read_bytes()).hexdigest(),p['sha256'])
        disposition=next(d for d in json.loads((parser.OUT/'dispositions.json').read_text())['sources'] if d['id']=='additional-source-langara-2023-24')
        self.assertEqual(disposition['status'],'imported')
        self.assertEqual(disposition['employeeRows'],891)


if __name__=='__main__':unittest.main()
