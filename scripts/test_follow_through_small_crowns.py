"""Source-backed regression tests for the fourteen reconstructed Crown schedules."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import unittest
import follow_through_small_crowns as crown

OUT=Path(__file__).resolve().parents[1]/'research/salaries/follow-through-small-crowns'

class SourceParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=json.loads((OUT/'sources.json').read_text())['sources']
        cls.bykey={s['file'].removesuffix('.json.gzip'):s for s in cls.sources}
        cls.rows={key:json.loads(gzip.decompress((OUT/s['file']).read_bytes())) for key,s in cls.bykey.items()}

    def test_every_native_source_replays_with_two_independent_readers(self):
        checked=0
        for key,source in self.bykey.items():
            if key=='bcfsa-2020-21':continue
            with self.subTest(source=key):
                words=json.loads(gzip.decompress((OUT/'evidence'/f'{key}.words.json.gzip').read_bytes()))
                primary,_=crown.coordinate_rows(words,key,source['employerSlug'])
                independent=crown.layout_rows((OUT/'evidence'/f'{key}.layout.txt').read_text(),key,source['employerSlug'])
                self.assertEqual(crown.counter(primary),crown.counter(independent))
                self.assertEqual(primary,self.rows[key]);checked+=len(primary)
        self.assertEqual(checked,4143)

    def test_automatic_and_column_ocr_replay_all112_scan_rows(self):
        primary,independent=crown.scan_rows()
        self.assertEqual(primary,independent)
        self.assertEqual(primary,self.rows['bcfsa-2020-21'])
        self.assertEqual(collections.Counter(r[5] for r in primary),{7:21,8:43,9:43,10:5})
        self.assertEqual(crown.sums(primary),[12494835,204709])
        proof=json.loads(gzip.decompress((OUT/'evidence/bcfsa-2020-21.rows.json.gzip').read_bytes()))
        self.assertEqual([r['normalized'] for r in proof],primary)
        self.assertTrue(all(r['allFieldsVisuallyReviewedAgainstOriginal'] and len(r['original300DpiPixelRect'])==4 for r in proof))
        self.assertEqual(len(proof),112)

    def test_board_and_reconciliation_rows_are_excluded_at_real_boundaries(self):
        for key,rows in self.rows.items():
            self.assertTrue(all(',' in r[1] and not any(c.isdigit() for c in r[1]) for r in rows),key)
            self.assertTrue(all(not any(t in r[1].lower() for t in ['consolidated','employees total','reconciling','board director']) for r in rows),key)
        self.assertEqual(self.rows['bcfsa-2019-20'][0][1],'Carter, Christopher')
        self.assertEqual(self.rows['pavco-2024-25'][0][1],'Adams, P')
        self.assertFalse(any(r[1]=='Elgar, C' for r in self.rows['bcfsa-2025-26']))

    def test_tight_two_column_expenses_do_not_split_at_header_width(self):
        rows=self.rows['bcib-2024-25']
        actual={r[1]:r for r in rows if r[5]==25}
        self.assertEqual(actual['Abdirahman, A'][3:5],[91150,16545])
        self.assertEqual(actual['Anderson, RW'][3:5],[107282,None])
        self.assertEqual(actual['Anderson, SW'][3:5],[77784,18980])
        self.assertEqual(actual['Achanta, VRGR'][3:5],[91973,27])
        self.assertEqual(len(rows),1122)

    def test_pavco_retains_real_titles_and_first_row_currency_symbols(self):
        first=self.rows['pavco-2024-25'][0]
        self.assertEqual(first,['bc-pavilion-corporation','Adams, P','Director, Global Partnerships',150188,7460,4])
        self.assertTrue(all(r[2] is not None for r in self.rows['pavco-2024-25']))
        self.assertTrue(all(r[2] is None for k,rows in self.rows.items() if not k.startswith('pavco') for r in rows))

    def test_null_zero_and_negative_expenses_remain_distinct(self):
        scan={r[1]:r for r in self.rows['bcfsa-2020-21']}
        self.assertEqual(scan['Desantis, Robert'][4],0)
        self.assertEqual(scan['Francis, Gavin'][4],0)
        self.assertEqual(scan['Ibarguen, Adolfo'][4],0)
        self.assertEqual(scan['Drury, Courtney'][4],-298)
        self.assertEqual(scan['Sherwood, David'][4],-822)
        self.assertIsNone(next(r[4] for r in self.rows['bcib-2020-21'] if r[1]=='Barker, Paula'))
        self.assertIsNone(crown.amount('-'));self.assertEqual(crown.amount('0'),0)

    def test_source_names_and_repeated_names_are_preserved(self):
        self.assertIn('Ong, Clarisse joy Sy',[r[1] for r in self.rows['bcfsa-2020-21']])
        self.assertIn('Bandila, l',[r[1] for r in self.rows['bcib-2022-23']])
        self.assertEqual(sum(r[1]=='Adams, S' for r in self.rows['bcfsa-2022-23']),2)
        self.assertEqual(sum(r[1]=='Baker, D' for r in self.rows['bcib-2023-24']),2)

    def test_asterisks_remain_as_source_cohort_evidence(self):
        proof=json.loads((OUT/'evidence/bcib-2024-25.json').read_text())
        markers=proof['sourceCohortMarkers']
        self.assertEqual(markers['markedNamedEmployees'],1066)
        self.assertEqual(markers['unmarkedNamedEmployees'],56)
        rows=self.rows['bcib-2024-25']
        self.assertFalse(any('*' in r[1] for r in rows))
        self.assertEqual(rows[markers['markedRowIndexes'][0]][1],'Abbott, JT')
        self.assertNotIn(next(i for i,r in enumerate(rows) if r[1]=='Achanta, VRGR'),markers['markedRowIndexes'])

    def test_fourteen_hashed_deterministic_payloads_and_every_receipt(self):
        self.assertEqual(len(self.sources),14)
        self.assertEqual(sum(len(r) for r in self.rows.values()),4255)
        fingerprints=set()
        for key,s in self.bykey.items():
            with self.subTest(source=key):
                data=(OUT/s['file']).read_bytes();normalized=gzip.decompress(data)
                self.assertEqual(crown.sha(data),s['dataSha256'])
                self.assertEqual(crown.sha(normalized),s['normalizedSha256'])
                self.assertEqual(gzip.compress(crown.json_bytes(self.rows[key],True),mtime=0),data)
                self.assertEqual(crown.sums(self.rows[key]),[s['totalRemuneration'],s['totalExpenses']])
                proofdata=(OUT/s['provenanceFile']).read_bytes()
                self.assertEqual(crown.sha(proofdata),s['provenanceSha256'])
                proof=json.loads(proofdata)
                self.assertTrue(proof['everyRowFieldMultisetEqual'])
                self.assertEqual(proof['primaryRowCount'],len(self.rows[key]))
                for evidence in proof['rawEvidenceFiles']:
                    self.assertEqual(crown.sha((OUT/evidence['file']).read_bytes()),evidence['sha256'])
                self.assertNotIn(s['sha256'],fingerprints);fingerprints.add(s['sha256'])
                self.assertTrue(s['retainCompiledPartition'])

    def test_partial_first_period_and_printed_residuals_are_public(self):
        first=self.bykey['bcfsa-2019-20']
        self.assertEqual(first['periodStart'],'2019-11-01');self.assertEqual(first['periodEnd'],'2020-03-31')
        self.assertIn('partial fiscal year',first['publicWarning'])
        expected={'bcfsa-2019-20':[0,1],'bcfsa-2020-21':[-3,-3],'pavco-2024-25':[6,2],'bcib-2020-21':[1,1],'bcib-2021-22':[6,2],'bcib-2022-23':[2,2],'bcib-2023-24':[3,3]}
        self.assertEqual(sum(bool(s.get('publicWarning')) for s in self.sources),7)
        for key,residual in expected.items():
            proof=json.loads((OUT/self.bykey[key]['provenanceFile']).read_text())
            self.assertEqual(proof['controls']['residualNamedMinusImplied'],residual)
            self.assertTrue(self.bykey[key]['publicWarning'])
        proof=json.loads((OUT/first['provenanceFile']).read_text())
        self.assertEqual(proof['controls']['residualNamedMinusDirect'],[-1,0])

    def test_all_assigned_reports_have_final_dispositions_and_official_links(self):
        leads=json.loads((OUT/'leads.json').read_text())
        disposition=json.loads((OUT/'dispositions.json').read_text())
        self.assertEqual({v['id'] for v in leads},{v['leadId'] for v in disposition['dispositions']})
        self.assertEqual(disposition['acceptedEmployeeRows'],4255)
        self.assertEqual(disposition['heldEmployeeReports'],0)
        self.assertTrue(all(not v['blockers'] and v['compiledRowsDeleted']==0 for v in disposition['dispositions']))
        indexes=json.loads((OUT/'evidence/index-checks.json').read_text())
        self.assertEqual(sum(len(v['reports']) for v in indexes),14)
        self.assertTrue(all(r['literalLinkPresent'] for v in indexes for r in v['reports']))
        self.assertEqual(json.loads((OUT/'evidence/duplicate-check.json').read_text())['matches'],[])

if __name__=='__main__':unittest.main()
