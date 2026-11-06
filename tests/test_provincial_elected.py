"""Run: python -m unittest discover -s tests -p 'test_provincial_elected.py'."""
import gzip, importlib.util, json, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('provincial',Path(__file__).resolve().parents[1]/'scripts/import-provincial-elected.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class ProvincialElectedTest(unittest.TestCase):
 def test_money_is_strict_and_retains_corrections(self):
  self.assertEqual(p.amount('(1,329)'),-1329)
  self.assertIsNone(p.amount('#N/A'))
  with self.assertRaises(ValueError):p.amount('approximately 10')
 def test_all_sources_reproduce_and_reconcile_controls(self):
  manifest=json.loads((p.BASE/'sources.json').read_text());controls=json.loads((p.BASE/'controls.json').read_text())
  self.assertEqual(len(manifest['sources']),39)
  self.assertEqual(sum(s['rowCount'] for s in manifest['sources']),2428)
  for s in manifest['sources']:
   with self.subTest(source=s['id']):
    original=(p.BASE/s['originalFile']).read_bytes();rows,audit=(p.parse_mla if 'members' in s['id'] else p.parse_ministers)(original)
    self.assertEqual(p.digest(original),controls[s['id']]['sha256'])
    self.assertEqual(rows,json.loads(gzip.decompress((p.BASE/s['file']).read_bytes())))
    self.assertEqual(audit,json.loads((p.BASE/s['auditFile']).read_text()))
    self.assertEqual(len(rows),controls[s['id']]['rowCount']);self.assertEqual(p.total(r[3] for r in rows),controls[s['id']]['totalRemuneration']);self.assertEqual(p.total(r[4] for r in rows),controls[s['id']]['totalDisclosedExpenses'])
    self.assertEqual(len({r[1] for r in rows}),len(rows))
 def test_negative_correction_and_continuation(self):
  rows,audit=p.parse_mla((p.BASE/'originals/fye-2009-members-compensation.csv').read_bytes())
  self.assertEqual(next(r[3] for r in rows if r[1]=='Austin, Robin'),98435)
  rows,audit=p.parse_mla((p.BASE/'originals/fye23-member-comp.csv').read_bytes())
  self.assertEqual(next(r[3] for r in rows if r[1]=='Anderson, Brittny'),124133)
 def test_stray_spreadsheet_cells_not_imported(self):
  rows,audit=p.parse_mla((p.BASE/'originals/fye21-members-comp.csv').read_bytes())
  self.assertEqual(len(rows),115);self.assertEqual(p.total(r[3] for r in rows),10177772)
  self.assertTrue(audit['publishedTotalControl']);self.assertEqual(len(audit['unattributedCellsExcluded']),84)
 def test_existing_deputies_are_not_reimported(self):
  audit=json.loads((p.BASE.parent/'provincial-administration/overlap-audit.json').read_text())
  self.assertEqual(sum(x['rowCount'] for x in audit['sources']),919)
  self.assertTrue(all(x['hashMatchesExisting'] for x in audit['sources']))
if __name__=='__main__':unittest.main()
