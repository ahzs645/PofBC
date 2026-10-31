from __future__ import annotations
from collections import Counter
import copy
import csv
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from stage_chc_recovery import BASE, ValidationError, csv_bytes, parse_row, stage_capture
from check_chc_pdf import reconstruct,ensure_headers

class RecoveryTests(unittest.TestCase):
    def get(self,year='2012-13'):
        return json.loads((BASE/'captures'/f'{year}.json').read_text())
    def test_real_captures_counts_and_totals(self):
        expected={'2012-13':(190,19718574,1089407,1,0),'2013-14':(226,23588724,1369304,3,-2),
                  '2014-15':(239,25533054,1370304,-3,2),'2015-16':(63,6651654,394765,3,-3),
                  '2016-17':(5,485097,30673,-1,1),'2017-18':(0,0,0,0,0)}
        for year,values in expected.items():
            with self.subTest(year=year):
                rows,r=stage_capture(self.get(year))
                self.assertEqual(tuple(r[k] for k in ('rowCount','namedRemuneration','namedExpenses','remunerationResidual','expenseResidual')),values)
                self.assertFalse(r['acceptedForPublication'])
    def test_full_candidate_count(self):
        self.assertEqual(sum(len(stage_capture(json.loads(p.read_text()))[0]) for p in (BASE/'captures').glob('*.json')),723)
    def test_zero_preserved(self):
        rows,_=stage_capture(self.get());r=next(x for x in rows if x['rawName']=='KR Harrison')
        self.assertEqual(r['expenses'],0);self.assertIsNone(r['position'])
    def test_compound_name_preserved(self):
        self.assertEqual(parse_row('J Van Zyll De Jong 76,937 0')[0],'J Van Zyll De Jong')
    def test_suffix_preserved(self):
        self.assertEqual(parse_row('F Gienger Sr. 126,529 2,130')[0],'F Gienger Sr.')
    def test_apostrophe_preserved(self):
        self.assertEqual(parse_row("DA O'Sullivan 105,733 6,622")[0],"DA O'Sullivan")
    def test_hyphen_and_period_preserved(self):
        self.assertEqual(parse_row('HJ St. Eloi 119,277 34,720')[0],'HJ St. Eloi')
        self.assertEqual(parse_row('BF Stamp-Vincent 108,301 30')[0],'BF Stamp-Vincent')
    def test_duplicate_initials_are_not_deduplicated(self):
        rows,_=stage_capture(self.get('2014-15'));same=[r for r in rows if r['rawName']=='JW Anderson']
        self.assertEqual([r['remuneration'] for r in same],[146855,93162])
    def test_exact_duplicate_multiplicity_preserved(self):
        d=self.get();line=d['pages'][0]['rowsText'].splitlines()[0];d['pages'][0]['rowsText']+=line+'\n'
        rows,r=stage_capture(d);self.assertEqual(len(rows),191);self.assertEqual(r['duplicateLookingExtraRows'],1)
        self.assertFalse(r['withinHypotheticalRoundingBound']);self.assertFalse(r['acceptedForPublication'])
    def test_malformed_money_rejected(self):
        for s in ['A Smith 12,34 0','A Smith 90,000.OO 0','A Smith 90,000 1,23','A Smith 090000 0','A Smith 90000 -']:
            with self.subTest(s=s),self.assertRaises(ValidationError):parse_row(s)
    def test_cents_are_not_truncated(self):
        with self.assertRaises(ValidationError):parse_row('A Smith 90,000.25 0')
    def test_missing_expense_not_zero_filled(self):
        with self.assertRaises(ValidationError):parse_row('A Smith 90,000')
    def test_threshold_not_accepted(self):
        for amount in (0,74999,75000):
            with self.assertRaises(ValidationError):parse_row(f'A Smith {amount} 0')
    def test_supplier_rejected(self):
        with self.assertRaises(ValidationError):parse_row('Workers Compensation Board 1189569')
    def test_aggregate_rejected_as_employee(self):
        with self.assertRaises(ValidationError):parse_row('Total 40922411 2357191')
    def test_missing_sheet(self):
        d=self.get();d['pages'].pop(1)
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_duplicate_physical_page(self):
        d=self.get();d['pages'][1]['pdfPage']=172
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_wrong_year(self):
        d=self.get();d['pages'][0]['periodHeader']=d['pages'][0]['periodHeader'].replace('2013','2014')
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_wrong_employer(self):
        d=self.get();d['pages'][0]['employerHeader']='POWEREX CORP.'
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_supplier_schedule_header(self):
        d=self.get();d['pages'][0]['scheduleHeader']='Schedule of Payments to Suppliers'
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_aggregate_only_is_not_missing(self):
        rows,r=stage_capture(self.get('2017-18'));self.assertEqual(rows,[])
        self.assertEqual(r['sourceControls']['totalRemuneration'],208410)
        self.assertEqual(r['status'],'aggregate-only-awaiting-pdf-verification')
    def test_aggregate_only_mismatch_rejected(self):
        d=self.get('2017-18');d['controls']['totalRemuneration']+=1
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_empty_named_capture_rejected(self):
        d=self.get('2017-18');d['captureType']='named-employee-candidates'
        with self.assertRaises(ValidationError):stage_capture(d)
    def test_no_balancing_row(self):
        rows,r=stage_capture(self.get('2016-17'));self.assertEqual(len(rows),5)
        self.assertEqual(sum(x['remuneration'] for x in rows),485097);self.assertEqual(r['remunerationResidual'],-1)
    def test_below_aggregate_never_becomes_row(self):
        rows,r=stage_capture(self.get('2015-16'))
        self.assertNotIn(r['sourceControls']['belowThresholdRemuneration'],[x['remuneration'] for x in rows])
    def test_csv_round_trip(self):
        rows,_=stage_capture(self.get());back=list(csv.DictReader(io.StringIO(csv_bytes(rows).decode())))
        self.assertEqual(len(rows),len(back));self.assertEqual(sum(int(r['expenses']) for r in back),1089407)
    def test_reader_column_reconstruction(self):
        words=[(25,150,30,160,'A'),(35,150,80,160,'Smith'),(200,150,250,160,'90,000'),(270,150,280,160,'0'),
               (330,150,335,160,'B'),(340,150,400,160,'Jones'),(500,150,550,160,'100,000'),(570,150,585,160,'20')]
        rows,unparsed=reconstruct(words,612,12)
        self.assertEqual(rows,[('A Smith',90000,0,12),('B Jones',100000,20,12)]);self.assertEqual(unparsed,[])
    def test_suspicious_reader_row(self):
        words=[(25,150,30,160,'A'),(35,150,80,160,'Smith'),(200,150,250,160,'12,34'),(270,150,280,160,'0')]
        rows,unparsed=reconstruct(words,612,12);self.assertEqual(rows,[]);self.assertEqual(len(unparsed),1)
    def test_reader_header_rejects_wrong_employer(self):
        with self.assertRaises(ValidationError):ensure_headers('POWEREX CORP.',self.get(),172)
    def test_byte_identical_rebuild(self):
        script=Path(__file__).with_name('stage_chc_recovery.py')
        with tempfile.TemporaryDirectory() as td:
            dirs=[Path(td)/'a',Path(td)/'b']
            for directory in dirs:
                subprocess.run([sys.executable,str(script),'--output',str(directory)],check=True,capture_output=True)
            a={p.name:p.read_bytes() for p in dirs[0].iterdir()};b={p.name:p.read_bytes() for p in dirs[1].iterdir()}
            self.assertEqual(a,b);self.assertEqual(len(a),26)
            for name,data in a.items():
                if name.endswith('.gzip'):self.assertEqual(gzip.decompress(data),a[name[:-5]])

if __name__=='__main__':unittest.main(verbosity=2)
