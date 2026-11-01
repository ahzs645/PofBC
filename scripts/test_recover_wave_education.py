#!/usr/bin/env python3
"""Regression fixtures use original independently extracted page evidence."""
import collections,gzip,json,unittest
import recover_wave_education as m

def evidence(sid):
 return json.loads(gzip.decompress((m.OUT/'evidence'/(sid+'.json.gzip')).read_bytes()))

class EducationRecoveryTests(unittest.TestCase):
 def test_missing_zero_and_negative_are_distinct(self):
  self.assertIsNone(m.money(''))
  self.assertIsNone(m.money('-'))
  self.assertEqual(m.money('0'),0)
  self.assertEqual(m.money('(4,268)'),-4268)
  self.assertEqual(m.money('-36'),-36)
 def test_ubc_wrapped_names_two_columns_and_row_count(self):
  ev=evidence('recovery-ubc-sofi-2025-26-employees');p=ev['pageEvidence'][0]
  a,_=m.primary_ubc(p['words'],42);b,_=m.secondary_ubc(p['popplerLayout'],42)
  self.assertEqual(a,b)
  self.assertEqual(len(a),43)
  byname={r[0]:r for r in a}
  self.assertEqual(byname['Abanto Salguero, Arleni Karina'][2:4],[147334,581])
  self.assertEqual(byname['Abramovay Ferraz Do Amaral, Claudio'][2:4],[382097,19749])
  self.assertEqual(byname['Addanki, Sheila Kumari Valli'][2:4],[99611,686])
 def test_ubc_duplicate_names_and_negative_source_cells_retained(self):
  ss=json.loads((m.OUT/'sources.json').read_text())['sources'];s=ss[0]
  rows=json.loads(gzip.decompress((m.OUT/s['file']).read_bytes()))
  self.assertEqual([r[3:5] for r in rows if r[1]=='Wilson, Brian'],[[139367,None],[264107,4198]])
  self.assertEqual(len([r for r in rows if r[4] is not None and r[4]<0]),11)
  self.assertEqual([r[4] for r in rows if r[1]=='McLean, Larissa'],[-4268])
 def test_salary_plus_benefits_is_separate_from_expense_inclusive_total(self):
  ev=evidence('recovery-coast-mountain-sofi-2024-25-employees');p=ev['pageEvidence'][0]
  a,proof=m.primary_college(p['words'],34,'coast-mountain','2024/25');b,bp=m.secondary_college(p['popplerLayout'],34,'coast-mountain','2024/25')
  self.assertEqual(a,b)
  self.assertEqual(a[0][2:4],[113427,2000])
  self.assertEqual(m.money(proof[0]['publishedExpenseInclusiveTotalToken']),115427)
  self.assertEqual(bp[0]['publishedExpenseInclusiveTotal'],115427)
  self.assertIsNone(next(r for r in a if r[0]=='Conway, Allison')[3])
 def test_offline_replay_all_cells_and_controls(self):
  m.verify(False)

if __name__=='__main__':unittest.main()
