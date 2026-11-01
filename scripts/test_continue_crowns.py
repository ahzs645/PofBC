"""Crown source fidelity checks; offline evidence needs no PDF/OCR engines."""
import collections,gzip,hashlib,json,unittest
from pathlib import Path
import continue_crowns as m

class CrownContinuationTests(unittest.TestCase):
 def test_missing_and_signed_cells(self):
  self.assertIsNone(m.money('‐'));self.assertIsNone(m.money('—'));self.assertEqual(m.money('0'),0);self.assertEqual(m.money('‐704'),-704);self.assertEqual(m.money('(311)'),-311);self.assertEqual(m.money('156.76'),156.76)
 def test_repeated_names_preserve_multiplicity(self):
  t='EMPLOYEE NAME REMUNERATION EXPENSES\nALI A.     80,001    0\nALI A.     80,001    0\n'
  self.assertEqual(len(m.parse_layout(t,'icbc')),2)
 def test_non_person_controls_do_not_become_employees(self):
  t='RECEIVER GEN. OF CANADA    32,520,826     0\nTOTAL FOR OVER $75,000    415,313,973    3,815,244\nOTHER UNDER $75,000    147,277,432    799,522\n'
  self.assertEqual(m.parse_layout(t,'icbc'),[])
 def test_transition_uses_total_not_components(self):
  t='ABBOTT M.    81,074   18,730   99,804    9,782\n'
  self.assertEqual(m.parse_layout(t,'icbc',transition=True),[['ABBOTT M.',99804,9782]])
 def test_literal_noncomma_housing_name(self):
  self.assertEqual(m.parse_layout('Celligoi R G     $ 79,207    $ 498','bc-housing'),[['Celligoi R G',79207,498]])
 def test_board_total_not_fee_or_expense(self):
  t='Richard J.M. Fyfe, KC (Victoria)    Board Chair     16+   1   $2,700    $6,000    $8,700\nTotal Board Member Remuneration    $2,700    $6,000    $8,700\n'
  self.assertEqual(m.parse_board_layout(t),([['Richard J.M. Fyfe, KC (Victoria)','Board Chair',8700]],8700))
 def test_board_component_conflict_fails(self):
  with self.assertRaisesRegex(ValueError,'component'):m.parse_board_layout('A Name (Victoria)    Director     $1,000   $2,000   $3,001\n')
 def test_all_retained_evidence_replays_byte_exactly(self):
  manifest=json.loads((m.OUT/'sources.json').read_text());specs={s['id']:s for s in json.loads((m.RESEARCH/'source-specs.json').read_text())}
  for source in manifest['sources']:
   with self.subTest(source=source['id']):
    rows,ev=m.replay(specs[source['id']],m.extract(specs[source['id']],offline=True));data=gzip.compress(m.compact(rows),mtime=0)
    self.assertEqual(hashlib.sha256(data).hexdigest(),source['dataSha256']);self.assertEqual(data,(m.OUT/source['file']).read_bytes());self.assertEqual(len(rows),source['rowCount']);self.assertTrue(ev['everyRowFieldAgreement'])
    self.assertEqual(source['sha256'],ev['originalPdfSha256'])
    if source['category']=='board-remuneration':self.assertTrue(all(r[4] is None for r in rows));self.assertIsNone(source['totalExpenses']);self.assertFalse(source['completeEmployeeSchedule'])
 def test_transitional_source_period_and_receiver(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources'];s=next(s for s in sources if s['id']=='continuation-crowns-icbc-2016-17')
  self.assertEqual((s['periodStart'],s['periodEnd'],s['reportingMonths']),('2016-01-01','2017-03-31',15));self.assertEqual(s['totalRemuneration'],281666625-23220971)
 def test_scope_and_literal_anomalies(self):
  D=json.loads((m.OUT/'sources.json').read_text());by={s['id']:s for s in D['sources']}
  for sid,name,value in [('continuation-crowns-bclc-2024-25','SUTHERLAND, TAMMY',-738),('continuation-crowns-bclc-2020-21','TURNER, TRICIA',-704),('continuation-crowns-royal-bc-museum-2024-25','Hardie,Colin',-311)]:
   s=by[sid];rows=json.loads(gzip.decompress((m.OUT/s['file']).read_bytes()));self.assertIn((name,value),[(r[1],r[4]) for r in rows]);self.assertIn('negative',s['publicWarning'].lower())
  for sid in ['continuation-crowns-icbc-2017-18','continuation-crowns-bclc-2017-18','continuation-crowns-royal-bc-museum-2023-24']:
   s=by[sid];self.assertTrue(s['retainCompiledPartition']);self.assertTrue(s['validation']['compiledPartitionRetained']);self.assertTrue(s['completeEmployeeSchedule']);self.assertTrue(s['validation']['completeEmployeeSchedule']);self.assertTrue(s['validation']['compiledPartitionRetentionReason'])

if __name__=='__main__':unittest.main()
