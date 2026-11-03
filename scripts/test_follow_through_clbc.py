import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import unittest
from follow_through_clbc import employee_lines,group_fingerprint,parse_line,decimal,gz_json

OUT=Path(__file__).resolve().parents[1]/'research/salaries/follow-through-clbc'

class ParserTests(unittest.TestCase):
    def test_board_and_aggregate_boundary_and_separate_total_column(self):
        pages=[['1. Members of the Board of Directors','Chair, A  100,000.00  20.00  100,020.00','2. Other Employees','Employee  Remuneration  Expenses  Total','Worker, B  80,000.00  12.34  80,012.34','Total Remuneration over $75,000  80,000.00  12.34  80,012.34','Suppliers, C  90,000.00  10.00  90,010.00']]
        rows=list(employee_lines(pages,False))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][:4],['Worker, B',Decimal('80000'),Decimal('12.34'),Decimal('80012.34')])

    def test_dash_and_explicit_zero_have_different_meaning(self):
        self.assertIsNone(parse_line('Doe, A  80,123  -')[2])
        self.assertEqual(parse_line('Doe, B  80,123  0')[2],Decimal(0))
        self.assertIsNone(decimal('-'))

    def test_original_initials_punctuation_and_hyphen_are_retained(self):
        self.assertEqual(parse_line("O'Toole, D. R - Bob  91,234  1,200")[0],"O'Toole, D. R - Bob")

    def test_duplicate_group_excludes_only_page_and_order(self):
        a=[['community-living-bc','A, B',None,80000,None,2],['community-living-bc','C, D',None,90000,0,3]]
        b=[[*r[:5],99] for r in reversed(a)]
        self.assertEqual(group_fingerprint(a),group_fingerprint(b))
        b[0][4]=None
        self.assertNotEqual(group_fingerprint(a),group_fingerprint(b))

    def test_table_of_contents_does_not_become_employee_rows(self):
        pages=[['For the Year Ended March 31, 2025','Schedule B - Employee Remuneration and Expenses','Schedule C - Board Members Remuneration and Expenses','Supplier, X  500,000  10'],['Schedule B - Employee Remuneration and Expenses','For the Year Ended March 31, 2025','Employee  Remuneration  Expenses','Actual, Y  80,000  1','Total for employees with remuneration exceeding $75,000  80,000  1']]
        self.assertEqual([r[0] for r in employee_lines(pages,True)],['Actual, Y'])

class PublishedCohortTests(unittest.TestCase):
    def test_all_twenty_reports_have_complete_exact_employee_controls(self):
        sources=json.loads((OUT/'sources.json').read_text())['sources']
        self.assertEqual(len(sources),20)
        self.assertEqual(sum(s['rowCount'] for s in sources),3218)
        self.assertEqual([s['rowCount'] for s in sources],[4,40,53,64,68,83,81,91,93,108,93,108,139,137,175,306,302,299,453,521])
        self.assertEqual(sources[0]['periodStart'],'2005-07-01')
        self.assertEqual(sources[0]['periodEnd'],'2006-03-31')
        for source in sources:
            with self.subTest(source=source['id']):
                data=(OUT/source['file']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(),source['dataSha256'])
                rows=json.loads(gzip.decompress(data));self.assertEqual(len(rows),source['rowCount'])
                self.assertEqual(gz_json(rows),data)
                self.assertTrue(all(r[0]=='community-living-bc' and r[2] is None and r[3]>75000 and isinstance(r[5],int) for r in rows))
                self.assertEqual(sum(Decimal(str(r[3])) for r in rows),Decimal(str(source['totalRemuneration'])))
                self.assertEqual(sum(Decimal(str(r[4] or 0)) for r in rows),Decimal(str(source['totalDisclosedExpenses'])))
                proof=json.loads((OUT/source['validation']['proofFile']).read_text())
                self.assertEqual(proof['payResidual'],0);self.assertEqual(proof['expenseResidual'],0)
                self.assertEqual(Decimal(proof['namedControl']['pay']),Decimal(str(source['totalRemuneration'])))
                self.assertEqual(Decimal(proof['namedControl']['expenses']),Decimal(str(source['totalDisclosedExpenses'])))
                self.assertFalse(proof['sourceFingerprintDuplicates']);self.assertFalse(proof['normalizedGroupDuplicates'])
                evidence=json.loads(gzip.decompress((OUT/proof['rowEvidenceFile']).read_bytes()))
                self.assertEqual(len(evidence),len(rows))
                self.assertEqual([r['name'] for r in evidence],[r[1] for r in rows])

    def test_every_scanned_row_has_original_pixel_and_independent_reading_evidence(self):
        for year,count in [('2008-09',64),('2010-11',83)]:
            proof=json.loads((OUT/'proof'/f'{year}.json').read_text())
            evidence=json.loads(gzip.decompress((OUT/proof['rowEvidenceFile']).read_bytes()))
            self.assertEqual(len(evidence),count)
            for r in evidence:
                self.assertTrue(r['visuallyReviewed'])
                self.assertTrue(r['ocrOriginalLine']);self.assertTrue(r['cleanedPsm6Line'])
                self.assertEqual(Decimal(r['pay'])+Decimal(r['expenses'] or '0'),Decimal(r['combinedTotal']))

    def test_every_native_row_retains_agreeing_independent_reader_fields(self):
        sources=json.loads((OUT/'sources.json').read_text())['sources'];count=0
        for source in sources:
            if source['year'] in ('2008/09','2010/11'):continue
            proof=json.loads((OUT/source['validation']['proofFile']).read_text())
            evidence=json.loads(gzip.decompress((OUT/proof['rowEvidenceFile']).read_bytes()))
            for row in evidence:
                p=parse_line(row['popplerLine']);m=parse_line(row['mupdfLine'])
                self.assertEqual(p,m);self.assertEqual(p[0],row['name'])
                self.assertEqual(p[1],Decimal(row['pay']))
                self.assertEqual(p[2],Decimal(row['expenses']) if row['expenses'] is not None else None)
                count+=1
        self.assertEqual(count,3071)

    def test_all_inventory_reports_have_a_final_disposition(self):
        inventory=json.loads((OUT/'inventory.json').read_text())
        dispositions=json.loads((OUT/'dispositions.json').read_text())
        self.assertEqual({r['id'] for r in inventory},{r['id'] for r in dispositions['reports']})
        self.assertTrue(all(r['status']=='accepted' and r['blocker'] is None for r in dispositions['reports']))

if __name__=='__main__':unittest.main()
