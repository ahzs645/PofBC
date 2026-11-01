#!/usr/bin/env python3
"""Guard source fidelity for the reviewed Crown salary import."""
import gzip,json,unittest
from pathlib import Path
from import_sector_crowns import OUT,SPEC,parse_layout,verify_pdf
class CrownSourceTests(unittest.TestCase):
 def test_independent_saved_pages_reproduce_every_field_and_control(self):
  for spec in SPEC:
   stem=f'inbc-{spec["end"]-1}-{str(spec["end"])[-2:]}'
   e=json.loads(gzip.decompress((OUT/'evidence'/f'{stem}.json.gzip').read_bytes()))
   rows,control=parse_layout(e['popplerLayoutText'])
   self.assertEqual(rows,[r['row'] for r in e['positionedRows']])
   self.assertEqual(control,e['namedSubtotals'])
   self.assertEqual(len(rows),spec['count'])
 def test_numeric_subtotal_cannot_become_employee(self):
  rows,control=parse_layout('2. Employees with renumeration and expenses exceeding $75,000.\nSmith, A  100,000  500\n  100,000  500\n')
  self.assertEqual(rows,[['Smith, A',100000,500]])
  self.assertEqual(control,[100000,500])
 def test_dropped_employee_amount_rejected(self):
  with self.assertRaises(ValueError):parse_layout('2. Employees\nSmith, A  100,000  500\nJones, B  90,00X  250\n  190,000  750\n')
 def test_missing_control_rejected(self):
  with self.assertRaises(ValueError):parse_layout('2. Employees\nSmith, A  100,000  500\n')
 def test_original_hash_is_mandatory(self):
  with self.assertRaisesRegex(ValueError,'hash differs'):verify_pdf(b'%PDF substituted',SPEC[0])
 def test_residuals_are_explicit_and_cells_unchanged(self):
  manifest=json.loads((OUT/'sources.json').read_text())
  self.assertEqual(sum(s['rowCount'] for s in manifest['sources']),41)
  self.assertEqual([[c['residual'] for c in s['validation']['printedControls']] for s in manifest['sources']],[[0,0],[1,0],[0,1]])
  self.assertTrue(all(s['publicWarning'] for s in manifest['sources'][1:]))
  last=json.loads(gzip.decompress((OUT/'inbc-2024-25.json.gzip').read_bytes()))
  self.assertEqual(last[0],['inbc','Chiew, B.',None,88713,None,29])
  first=json.loads(gzip.decompress((OUT/'inbc-2022-23.json.gzip').read_bytes()))
  self.assertIn(['inbc','Deering, D',None,117575,8563,28],first)
 def test_compiled_replacement_has_exact_complete_cohort_and_fingerprint(self):
  import hashlib
  from collections import Counter
  evidence=json.loads((OUT/'inbc-overlap.json').read_text())
  selected=evidence['selectedRows']
  self.assertEqual(Counter(map(tuple,selected)),Counter(map(tuple,evidence['verifiedSourceRows'])))
  self.assertEqual(evidence['officialMatchesByPeriod'],{'2022/23':9,'2023/24':0,'2024/25':0})
  digest=hashlib.sha256(json.dumps(selected,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
  manifest=json.loads((OUT/'sources.json').read_text())
  rule=manifest['compiledReplacements'][0]
  self.assertEqual(rule['selectedRowsSha256'],digest)
  self.assertEqual((rule['compiledYear'],rule['replacementYear'],rule['expectedRows'],rule['expectedRetainedRows']),('2023/24','2022/23',9,0))
  self.assertEqual(rule['sourceDataSha256'][manifest['sources'][0]['id']],manifest['sources'][0]['dataSha256'])
if __name__=='__main__':unittest.main()
