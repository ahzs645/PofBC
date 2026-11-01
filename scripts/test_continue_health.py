"""Regression checks for source-faithful health board extraction."""
import gzip, json, unittest
from pathlib import Path
import continue_health as m

class HealthContinuationTests(unittest.TestCase):
 def test_offline_replay_every_cell_and_artifact(self):
  m.run(check_only=True)
  for source in json.loads((m.OUT/'sources.json').read_text())['sources']:
   self.assertIsInstance(source['notes'],list)
   self.assertTrue(all(isinstance(note,str) for note in source['notes']))
 def test_monetary_unknown_zero_negative_and_two_values_guard(self):
  self.assertIsNone(m.money(' $ - '));self.assertIsNone(m.money(''))
  self.assertEqual(m.money('$0'),0);self.assertEqual(m.money('(309)'),-309)
  for bad in ['734 172,169','1,200 7','unknown','500/day']:
   with self.assertRaises(ValueError):m.money(bad)
 def test_board_pay_omits_expense_inclusive_total(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  s=next(s for s in sources if s['id']=='northern-health-board-2021-22')
  rows=json.loads(gzip.decompress((m.OUT/s['file']).read_bytes()))
  nyce=next(r for r in rows if r[1]=='Nyce, Colleen')
  self.assertEqual(nyce[3:],[37000,-309,1])
  self.assertEqual(s['validation']['missingExpenseRows'],7)
 def test_unknown_remuneration_row_held_without_zero(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  s=next(s for s in sources if s['id']=='interior-health-board-2023-24')
  self.assertFalse(s['completeBoardSchedule'])
  held=s['validation']['heldUnknownRemunerationRows']
  self.assertEqual([(r['row'][1],r['row'][3]) for r in held],[('Halpenny, Robert Lorne',None)])
  self.assertEqual(s['rowCount'],11)
 def test_literal_whole_dollar_control_disagreements_retained(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  s=next(s for s in sources if s['id']=='northern-health-board-2024-25')
  self.assertEqual((s['validation']['remunerationResidual'],s['validation']['expensesResidual']),(1,-1))
  rows=json.loads(gzip.decompress((m.OUT/s['file']).read_bytes()))
  self.assertEqual(next(r[3] for r in rows if r[1]=='Kurjata, John'),24459)
 def test_annotation_removal_preserves_core_punctuation(self):
  self.assertEqual(m.clean_name('LeFebvre, Alain 4'),'LeFebvre, Alain')
  self.assertEqual(m.clean_name('Killam, Stephanie (note 2)'),'Killam, Stephanie')
  self.assertEqual(m.clean_name('Roundsville, Dennis *'),'Roundsville, Dennis *')

if __name__=='__main__':unittest.main()
