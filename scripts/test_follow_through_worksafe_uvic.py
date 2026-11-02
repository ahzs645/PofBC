#!/usr/bin/env python3
"""Regression checks for six complete original-backed employee cohorts."""
from collections import Counter
import gzip
import json
from pathlib import Path
import unittest

import follow_through_worksafe_uvic as parser


class ParserRegression(unittest.TestCase):
    def test_missing_zero_negative_money_distinctions(self):
        self.assertIsNone(parser.money('-'))
        self.assertIsNone(parser.money(''))
        self.assertEqual(parser.money('0'), 0)
        self.assertEqual(parser.money('(304)'), -304)
        self.assertEqual(parser.money('125,010'), 125010)
        with self.assertRaises(ValueError):
            parser.money('3O4')

    def test_two_column_footnotes_and_recoveries(self):
        s = {**parser.specs()[3], 'firstPage':1, 'lastPage':1}
        rows=parser.parse_layout(['García, Ana       75,000 *     -       Lee, Ming      125,010      (304) **'],s)
        self.assertEqual(rows, [[s['employerSlug'],'García, Ana',None,75000,None,1],[s['employerSlug'],'Lee, Ming',None,125010,-304,1]])

    def test_initial_duplicates_are_observations(self):
        s={**parser.specs()[0], 'firstPage':1,'lastPage':1}
        rows=parser.parse_layout(['Lee, J        100,001       0\nLee, J        100,002       -'],s)
        self.assertEqual(len(rows),2)
        self.assertEqual([r[4] for r in rows],[0,None])

    def test_aggregate_cannot_become_employee(self):
        s={**parser.specs()[0], 'firstPage':1,'lastPage':1}
        text='Total employees with remuneration over $75 000       314,770,529       8,978,354\nTotal employees with remuneration $75 000 or less       77,716,670       713,046\nTotal        392,487,199       9,691,400'
        self.assertEqual(parser.parse_layout([text],s),[])
        with self.assertRaises(ValueError):
            parser.parse_layout(['Unclassified Employee       100,001       30'],s)

    def test_deterministic_serialization(self):
        rows=[['workers-compensation-board','Lee, J',None,100001,None,92]]
        raw,a=parser.packed(rows);_,b=parser.packed(rows)
        self.assertEqual(a,b)
        self.assertEqual(gzip.decompress(a),raw)


class FrozenOriginalEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=parser.OUT
        cls.manifest=json.loads((cls.out/'sources.json').read_text())
        cls.sources={s['id']:s for s in cls.manifest['sources']}

    def test_complete_six_source_inventory_and_periods(self):
        self.assertEqual(self.manifest['rowSchema'],parser.SCHEMA)
        self.assertEqual(len(self.sources),6)
        dispositions=json.loads((self.out/'dispositions.json').read_text())['sources']
        self.assertEqual({d['id'] for d in dispositions},{'additional-source-'+s['key'] for s in parser.specs()})
        self.assertEqual(sum(s['rowCount'] for s in self.sources.values()),14715)
        for source in self.sources.values():
            if source['periodType']=='calendar':
                self.assertEqual(source['periodStart'],source['year']+'-01-01')
                self.assertEqual(source['periodEnd'],source['year']+'-12-31')
            else:
                self.assertTrue(source['periodStart'].endswith('-04-01'))
                self.assertTrue(source['periodEnd'].endswith('-03-31'))

    def test_every_frozen_original_row_is_independently_replayable(self):
        for spec in parser.specs():
            with self.subTest(source=spec['key']):
                source=self.sources[spec['key']+'-sofi-employees']
                data=(self.out/source['file']).read_bytes()
                rows=json.loads(gzip.decompress(data))
                self.assertEqual(parser.digest(data),source['dataSha256'])
                self.assertEqual(parser.digest(gzip.decompress(data)),source['normalizedSha256'])
                evidence_data=(self.out/source['validation']['originalBackedEvidenceFile']).read_bytes()
                self.assertEqual(parser.digest(evidence_data),source['validation']['originalBackedEvidenceSha256'])
                evidence=json.loads(gzip.decompress(evidence_data))
                self.assertEqual(evidence['sourceSha256'],spec['sha256'])
                self.assertEqual(Counter(map(tuple,rows)),Counter(tuple(r['row']) for r in evidence['coordinateRows']))
                self.assertEqual(rows,evidence['independentLayoutRows'])
                pages=['']*spec['lastPage']
                for p,t in evidence['independentLayoutPages'].items():pages[int(p)-1]=t
                self.assertEqual(parser.parse_layout(pages,spec),rows)
                for original in evidence['coordinateRows']:
                    row=original['row']
                    self.assertEqual(parser.money(original['remunerationCell']['text']),row[3])
                    self.assertEqual(parser.money(original['expenseCell']['text']),row[4])
                    self.assertEqual(parser.name(' '.join(w['text'] for w in original['nameWords'])),row[1])
                self.assertEqual(sum(r[3] for r in rows),source['totalRemuneration'])
                self.assertEqual(sum(r[4] or 0 for r in rows),source['totalDisclosedExpenses'])
                self.assertEqual(Counter(r[5] for r in rows),Counter({int(k):v for k,v in source['validation']['sourceRowsPerPhysicalPage'].items()}))
                self.assertEqual({r[5] for r in rows},set(range(spec['firstPage'],spec['lastPage']+1)))
                control=json.loads((self.out/'controls'/(spec['key']+'.json')).read_text())
                expected=parser.source_record(spec,rows,control['checks'],gzip.decompress(data),data,source['validation']['originalBackedEvidenceSha256'],source['validation']['visualReceiptSha256'])
                self.assertEqual(source,expected)

    def test_source_residuals_are_frozen_and_public(self):
        for spec in parser.specs():
            source=self.sources[spec['key']+'-sofi-employees'];v=source['validation'];expected=parser.REVIEWED[spec['key']]
            self.assertEqual((source['rowCount'],source['totalRemuneration'],source['totalDisclosedExpenses'],v['remunerationDifference'],v['expensesDifference']),expected[:5])
            if expected[3] or expected[4]:
                self.assertIn('publicWarning',source)
                self.assertIn('no cell is adjusted',source['publicWarning'])
            self.assertFalse(v['roundingComparisonOnly']['causeEstablished'])
            self.assertFalse(v['roundingComparisonOnly']['valuesAdjusted'])
        uvic=self.sources['uvic-2023-24-sofi-employees']
        self.assertEqual(uvic['validation']['printedNamedPlusBelowMinusGrandRemuneration'],1)
        self.assertEqual(self.sources['uvic-2019-20-sofi-employees']['validation']['atThresholdRows'],1)

    def test_all_rendered_receipts_match_artifacts(self):
        for source in self.sources.values():
            path=self.out/source['validation']['visualReceiptFile']
            self.assertEqual(parser.digest(path.read_bytes()),source['validation']['visualReceiptSha256'])
            receipt=json.loads(path.read_text())
            self.assertEqual(receipt['sourceSha256'],source['sha256'])
            rendered={p['pdfPage'] for p in receipt['pages']}
            self.assertTrue(set(source['pages']).issubset(rendered))
            for artifact in receipt['artifacts']:
                self.assertEqual(parser.digest((self.out/artifact['file']).read_bytes()),artifact['sha256'])

    def test_existing_original_sources_checked(self):
        receipt=json.loads((self.out/'duplicate-check.json').read_text())
        self.assertGreater(len(receipt['manifestsChecked']),60)
        self.assertEqual(receipt['duplicateAcceptedCohorts'],[])


if __name__=='__main__':
    unittest.main()
