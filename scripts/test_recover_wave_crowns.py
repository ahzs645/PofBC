"""Regression checks for original cell boundaries, transition periods and scope exclusions."""
import importlib.util
import unittest
from pathlib import Path
SPEC=importlib.util.spec_from_file_location('recovery_crowns',Path(__file__).with_name('recover_wave_crowns.py'))
C=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(C)

class SourceCellTests(unittest.TestCase):
 def test_unbalanced_parentheses_double_negative_and_malformed_grouping_fail(self):
  for value in ['(25','25)','(-25)','100,00']:
   with self.subTest(value=value),self.assertRaises(ValueError):C.amount(value)
 def test_dash_expenses_remain_unknown_while_numeric_zero_and_negative_are_literal(self):
  rows,_=C.parse_layout('  Smith, Alex    100,001    -\n  Smith, Bea    100,002    0\n  Smith, Cal    100,003    (25)')
  self.assertEqual(rows,[['Smith, Alex',100001,None],['Smith, Bea',100002,0],['Smith, Cal',100003,-25]])
 def test_transition_uses_published_fifteen_month_total_without_inventing_missing_component(self):
  rows,components=C.parse_layout('  Smith, Alex    100,000    -    100,000    12',True)
  self.assertEqual(rows,[['Smith, Alex',100000,12]])
  self.assertEqual(components,[[100000,None,100000,12]])
 def test_wrapped_aggregate_caption_and_accrual_control_cannot_become_people(self):
  rows,_=C.parse_layout('  in 15 months, but less than $75,000 in 12 months    6,540,376    1,597,573    8,137,949    107,435',True)
  self.assertEqual(rows,[])
  self.assertFalse(C.person('Accruals, leave liability, and secondments'))
 def test_coordinate_reader_rejects_an_extra_compensation_column(self):
  def word(x,text):return [x,10,x+8,20,text,0,0,0]
  ws=[word(10,'Smith,'),word(40,'Alex'),word(90,'100,001'),word(130,'50'),word(170,'10')]
  with self.assertRaisesRegex(ValueError,'Unexpected row columns'):C.parse_words(ws)
 def test_changed_page_set_fails_before_replaying_an_incomplete_schedule(self):
  with self.assertRaisesRegex(ValueError,'page set changed'):
   C.replay({'sha256':'a','pages':[1,2]},{'sourceSha256':'a','pages':[{'pdfPage':1}]})
 def test_changed_original_fingerprint_cannot_reuse_cached_evidence(self):
  with self.assertRaisesRegex(ValueError,'Evidence source changed'):
   C.replay({'sha256':'a','pages':[1]},{'sourceSha256':'b','pages':[]})

if __name__=='__main__':unittest.main()
