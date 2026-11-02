"""Actual municipal recovery regressions; no changing source cells to match controls."""
import gzip,json,unittest
from pathlib import Path
from finish_salary_municipal import money,tesseract_read,paddle_read
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/"research/salaries/queue-completion-2026-11-01/municipal"
class SourceRegressions(unittest.TestCase):
 def test_explicit_zero_missing_detection_and_source_dash_are_distinct(self):
  self.assertEqual(money("0"),{"kind":"number","value":0,"raw":"0"})
  self.assertEqual(money("—")["kind"],"explicit-dash")
  self.assertEqual(money("")["kind"],"missing-detection")
  self.assertIsNone(money("")["value"])
 def test_actual_mission_ocr_glyph_is_not_repaired_as_currency(self):
  self.assertEqual(money("§,203")["kind"],"unparsed")
  self.assertEqual(money("5,203")["value"],5203)
 def test_both_independent_geometry_readers_keep_every_staged_row(self):
  d=json.loads(gzip.decompress((AREA/"reader-draft.json.gzip").read_bytes()))
  self.assertEqual(sum(len(s["tesseractRows"]) for s in d["sections"]),835)
  self.assertEqual(sum(len(s["paddleRows"]) for s in d["sections"]),835)
  for section in d["sections"]:
   self.assertTrue(section["equalRowCounts"])
   expected=section["layout"].get("expectedRows")
   if expected is not None:self.assertEqual(len(section["tesseractRows"]),expected)
 def test_creston_literal_cells_are_not_balanced_or_zero_imputed(self):
  rows=json.loads(gzip.decompress((ROOT/"research/salaries/queue-completion-municipal/creston-2024-employee-remuneration.json.gzip").read_bytes()))
  self.assertEqual(len(rows),27)
  self.assertEqual((sum(r[3] for r in rows)-2685008,sum(r[4] for r in rows)-61044),(-12,-10))
  self.assertEqual(sum(r[4]==0 for r in rows),13)
  self.assertFalse(any(r[4] is None for r in rows))
  self.assertEqual(rows[11][3],77585)
  self.assertEqual(rows[10][1],"Fuller, C. Terrence")
  self.assertEqual(rows[26][1],"Zieffle, Brad")
  self.assertEqual(rows[25][1:3],["Jeff Webb","Waste Water Treatment Plan Operator"])
 def test_creston_old_council_and_compiled_scopes_are_preserved(self):
  spec=json.loads((AREA/"creston-source-spec.json").read_text())
  self.assertEqual(spec["scope"],"employee-remuneration")
  self.assertTrue(spec["retainCompiledPartition"])
  self.assertEqual(spec["periodStart"],"2024-01-01")
  self.assertIn("causes remain unresolved",spec["publicWarning"])
if __name__=="__main__":unittest.main()

