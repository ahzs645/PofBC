#!/usr/bin/env python3
"""Offline integrity/regression tests for the recovered Assembly staff schedules."""
import gzip,hashlib,importlib.util,json,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('recovery',Path(__file__).with_name('recover-assembly-staff.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AssemblyStaffTests(unittest.TestCase):
 def test_all_originals_and_normalized_rows(self):
  sources=json.loads((m.DEST/'sources.json').read_text())['sources']
  self.assertEqual(sum(s['rowCount'] for s in sources),743)
  for s in sources:
   raw=(m.DEST/s['originalFile']).read_bytes();data=(m.DEST/s['file']).read_bytes()
   self.assertTrue(raw.startswith(b'%PDF'))
   self.assertEqual(m.digest(raw),s['sha256']);self.assertEqual(m.digest(data),s['dataSha256'])
   parsed,total,residual=m.parse(m.DEST/s['originalFile'])
   self.assertEqual(parsed,json.loads(gzip.decompress(data)))
   self.assertEqual(sum(r[3] for r in parsed),s['totalRemuneration'])
   self.assertEqual(residual,s['validation']['namedRemunerationResidual'])
   self.assertEqual(total,s['validation']['publishedTotalRemuneration'])
   self.assertTrue(all(r[0]==m.SLUG and r[4] is None for r in parsed))
 def test_names_preserved_and_no_identity_inference(self):
  rows=json.loads(gzip.decompress((m.DEST/'2024-25.json.gzip').read_bytes()))
  self.assertIn('Nezhad, Sahra',[r[1] for r in rows])
  self.assertNotIn('Zangeneh Nezhad, Sahra',[r[1] for r in rows])
if __name__=='__main__':unittest.main()
