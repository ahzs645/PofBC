#!/usr/bin/env python3
"""Offline regression tests for original postsecondary table boundaries and money."""
import gzip
import json
import unittest
from continue_education import OUT, money, primary, secondary

class EducationTests(unittest.TestCase):
    def evidence(self,sid):
        return json.loads((OUT/'evidence'/f'{sid}.json').read_text())

    def test_missing_is_distinct_from_numeric_zero_and_negative(self):
        self.assertIsNone(money('‐'))
        self.assertIsNone(money(''))
        self.assertEqual(money('0.00'),0)
        self.assertEqual(money('(807.55)'),-807.55)
        self.assertEqual(money('-40.00'),-40)
        with self.assertRaises(AssertionError):money('unknown')

    def test_expense_inclusive_total_is_never_remuneration(self):
        line='Example, Person      100,000.25      125.30       100,125.55'
        rows,_=secondary(line,4,'douglas-college')
        self.assertEqual(rows,[['Example, Person',None,100000.25,125.3,4]])
        with self.assertRaises(AssertionError):secondary(line.replace('100,125.55','100,126.55'),4,'douglas-college')

    def test_reversed_viu_columns_and_expense_inclusive_total(self):
        rows,_=secondary('Example, Person      -      101,000.22     101,000.22',11,'vancouver-island-university')
        self.assertEqual(rows,[['Example, Person',None,101000.22,None,11]])

    def test_ufv_final_page_retains_named_employees_above_board(self):
        e=self.evidence('ufv-sofi-2023-24-employees');p=next(x for x in e['pageEvidence'] if x['physicalPage']==18)
        a,_=primary(p['words'],18,e['parserLayout'],False,'university-of-the-fraser-valley')
        b,_=secondary(p['popplerLayout'],18,'university-of-the-fraser-valley')
        self.assertEqual(a,b)
        self.assertEqual(len(a),23)
        self.assertEqual(a[0][0],'Wilbur, Amea')
        self.assertEqual(a[-1][0],'Zonneveld, Holly')
        self.assertNotIn('Crawford, Stacey',[r[0] for r in a])

    def test_camosun_partial_flags_and_retained_compiled_scope(self):
        ss=json.loads((OUT/'sources.json').read_text())['sources']
        for s in ss:
            if s['employerSlug']!='camosun-college':continue
            self.assertFalse(s['completeEmployeeSchedule'])
            self.assertFalse(s['validation']['completeEmployeeSchedule'])
            self.assertIn('board',s['publicWarning'].lower())
            if s['year'] in ['2017/18','2020/21','2023/24']:
                self.assertTrue(s['retainCompiledPartition'])
                self.assertTrue(s['validation']['compiledPartitionRetained'])

    def test_duplicate_and_literal_source_anomaly_preserved(self):
        s=next(s for s in json.loads((OUT/'sources.json').read_text())['sources'] if s['id']=='okanagan-sofi-2024-25-employees')
        rows=json.loads(gzip.decompress((OUT/s['file']).read_bytes()))
        self.assertEqual(len([r for r in rows if r[1]=='Wood, James']),2)
        self.assertIn('., Mohammed',[r[1] for r in rows])

    def test_ecu_total_remuneration_heading_does_not_create_total_column(self):
        from continue_education_supplemental import OUT as supplement
        e=json.loads((supplement/'evidence/ecu-sofi-2024-25-employees.json').read_text());p=e['pageEvidence'][0]
        a,_=primary(p['words'],3,e['parserLayout'],True,'emily-carr-university')
        b,_=secondary(p['popplerLayout'],3,'emily-carr-university')
        self.assertEqual(a,b)
        self.assertEqual(a[0],['Abbott, Amory',None,108061.87,1188.64,3])
        self.assertNotIn('Avison, Don',[r[0] for r in a])

if __name__=='__main__':unittest.main()
