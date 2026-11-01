import gzip,json,unittest
import resolve_held_education as m
class NicResolutionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((m.OUT/'sources.json').read_text())['sources'][0];cls.rows=json.loads(gzip.decompress((m.OUT/cls.s['file']).read_bytes()));cls.ev=json.loads(gzip.decompress((m.OUT/cls.s['validation']['evidenceFile']).read_bytes()))
 def test_five_complete_pages_and_exact_controls(self):
  self.assertEqual(len(self.rows),136);self.assertEqual(self.s['validation']['rowCountsByPdfPage'],{'26':14,'27':36,'28':36,'29':36,'30':14})
  self.assertEqual([sum(r[3] for r in self.rows),sum(r[4] or 0 for r in self.rows)],[13045792,543386]);self.assertEqual(self.s['validation']['namedControlResidualRowSumMinusPrinted'],[0,0])
 def test_hidden_white_titles_are_not_positions(self):
  self.assertTrue(all(r[2] is None for r in self.rows));self.assertGreater(sum(len(p['excludedWhiteTextSpans']) for p in self.ev['pages']),100)
  self.assertTrue(any('Media/Graphic Design' in s['text'] for p in self.ev['pages'] for s in p['excludedWhiteTextSpans']))
 def test_missing_is_not_zero(self):
  self.assertIsNone(m.money('-'));self.assertEqual(m.money('0'),0);self.assertEqual(m.money('(17)'),-17)
  self.assertIsNone(next(r for r in self.rows if r[1]=='Ackland, Shirley')[4]);self.assertEqual(next(r for r in self.rows if r[1]=='Blacquiere, Ashley')[4],63)
 def test_signed_scan_corroborates_only_actual_surviving_rows(self):
  self.assertEqual([c['rowCount'] for c in self.ev['signedScanCorroboration']],[36,36])
  for c in self.ev['signedScanCorroboration']:
   self.assertEqual(m.scan_rows(c['rawTesseractText'],c['archivedPackagePhysicalPage']),[r for r in self.rows if r[5]==c['archivedPackagePhysicalPage']])
 def test_truncated_package_is_never_marked_complete(self):
  self.assertTrue(self.s['completeEmployeeSchedule']);self.assertFalse(self.s['sourcePackageComplete']);self.assertIn('3,739,511',self.s['publicWarning']);self.assertEqual(self.ev['originalByteLength'],1048576);self.assertEqual(self.ev['originalReportedLength'],3739511)
 def test_separate_complete_board_scope(self):
  bs=json.loads((m.OUT/'sources.json').read_text())['sources'][1];rows=json.loads(gzip.decompress((m.OUT/bs['file']).read_bytes()))
  self.assertEqual(bs['category'],'board-remuneration');self.assertEqual(len(rows),15);self.assertTrue(bs['completeBoardSchedule']);self.assertFalse(bs['completeEmployeeSchedule']);self.assertTrue(all(r[2] is None for r in rows));self.assertIsNone(next(r for r in rows if r[1]=='Jain, Vikas')[4]);self.assertEqual([sum(r[3] for r in rows),sum(r[4] or 0 for r in rows)],[16375,12727])
 def test_full_independent_replay(self):m.verify(False)
if __name__=='__main__':unittest.main()
