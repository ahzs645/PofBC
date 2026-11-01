#!/usr/bin/env python3
"""Source fidelity guards for Capital/Cowichan salary recovery."""
import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from parse_wave_capital import BASE,money,cents,extract,read_table
class WaveCapitalTests(unittest.TestCase):
 def test_currency_preserves_missing_zero_negative_and_cents(self):
  self.assertIsNone(money('-'));self.assertIsNone(money(''));self.assertEqual(money('0.00'),0)
  self.assertEqual(money('(1,234.56)'),-1234.56);self.assertEqual(money('-2.50'),-2.5);self.assertEqual(cents(money('98,485.65')),9848565)
  with self.assertRaises(ValueError):money('75,OOO')
 def test_source_hash_change_rejected_before_table_read(self):
  spec=json.loads((BASE/'reviewed-layouts.json').read_text())['reports'][0]
  with tempfile.NamedTemporaryFile() as f:
   f.write(b'%PDF substituted');f.flush()
   with self.assertRaisesRegex(ValueError,'Original hash changed'):extract(spec,Path(f.name))
 def test_all_reviewed_rows_match_saved_engine_fields(self):
  m=json.loads((BASE/'sources.json').read_text());self.assertEqual(sum(s['rowCount'] for s in m['sources']),547)
  for s in m['sources']:
   ev=json.loads(gzip.decompress((BASE/s['validation']['evidenceFile']).read_bytes()))
   rows=json.loads(gzip.decompress((BASE/s['file']).read_bytes()))
   for row,e in zip(rows,ev['rows']):
    self.assertEqual(e['pymupdf']['values'],e['poppler']['values'])
    self.assertEqual(row[1:5],[e['fields']['name'],e['fields'].get('position'),e['fields']['pay'],e['fields'].get('expenses')])
   self.assertEqual(len(rows),s['rowCount']);self.assertEqual(hashlib.sha256((BASE/s['file']).read_bytes()).hexdigest(),s['dataSha256'])
 def test_unknown_below_threshold_expenses_do_not_become_zero_control(self):
  m=json.loads((BASE/'sources.json').read_text());s=next(s for s in m['sources'] if s['employerSlug']=='district-of-highlands' and s['category']=='employee-remuneration')
  self.assertIsNone(s['validation']['sourceControls']['below'][1]);self.assertIsNone(s['validation']['printedControls'][1]['printedControl']);self.assertIsNone(s['validation']['printedControls'][1]['residual'])
 def test_expense_inclusive_total_cannot_replace_pay(self):
  rows=json.loads(gzip.decompress((BASE/'town-of-lake-cowichan-2025-employee-remuneration.json.gzip').read_bytes()))
  self.assertEqual(rows[0][3:5],[80737.92,493.87]);self.assertNotEqual(rows[0][3],81231.79)
 def test_departments_are_not_invented_job_titles(self):
  rows=json.loads(gzip.decompress((BASE/'township-of-esquimalt-2025-employee-remuneration.json.gzip').read_bytes()));self.assertTrue(all(r[2] is None for r in rows))
 def test_published_numeric_total_survives_unknown_benefit_component(self):
  e=json.loads(gzip.decompress((BASE/'evidence/city-of-colwood-2025-employee-remuneration.json.gzip').read_bytes()))
  row=next(r['fields'] for r in e['rows'] if r['fields']['name']=='POIRIER, SABRINA');self.assertIsNone(row['benefits']);self.assertEqual(row['pay'],107847)
 def test_residuals_stay_visible_without_cause_inference(self):
  m=json.loads((BASE/'sources.json').read_text());nonzero=[s for s in m['sources'] if any(c['residual'] for c in s['validation']['printedControls'])]
  self.assertEqual(len(nonzero),6);self.assertTrue(all(s['publicWarning'] and 'cause is unresolved' in s['publicWarning'] for s in nonzero))
 def test_reviewed_colwood_approval_is_explicit_despite_watermark(self):
  m=json.loads((BASE/'sources.json').read_text());s=next(s for s in m['sources'] if s['employerSlug']=='city-of-colwood');e=s['validation']['publicationEvidence'];self.assertEqual(e['pdfPage'],4);self.assertEqual(e['approvalDate'],'2026-06-29');self.assertEqual(len(e['signaturesVisuallyReviewed']),2);self.assertEqual(e['salaryTableWatermark'],'DRAFT')
 def test_rendered_edges_guard_summary_text_in_last_title(self):
  ev=json.loads(gzip.decompress((BASE/'evidence/town-of-view-royal-2025-employee-remuneration.json.gzip').read_bytes()))
  layout=ev['layout']['layouts'][0]
  words=[w for row in ev['rows'] for w in row['pymupdf']['words']]
  last=ev['rows'][-1]['pymupdf']['anchorY']
  words.append({'x':190,'y':last+.1,'right':250,'bottom':last+7,'t':'Consolidated'})
  with self.assertRaisesRegex(ValueError,'Rendered source edge changed'):read_table(words,layout)
 def test_all_text_fields_reject_financial_currency_markers(self):
  m=json.loads((BASE/'sources.json').read_text())
  for source in m['sources']:
   for row in json.loads(gzip.decompress((BASE/source['file']).read_bytes())):
    self.assertNotIn('$',row[1]);self.assertNotIn('$',row[2] or '')
 def test_material_conflict_is_held_even_when_subtotals_match(self):
  m=json.loads((BASE/'sources.json').read_text())
  self.assertFalse(any(s['employerSlug']=='town-of-lake-cowichan' and s['year']=='2024' and s['category']=='employee-remuneration' for s in m['sources']))
  ev=json.loads(gzip.decompress((BASE/'evidence/town-of-lake-cowichan-2024-employee-remuneration-held.json.gzip').read_bytes()))
  self.assertEqual(ev['individualRowsAccepted'],0);self.assertEqual(ev['residuals'],[0,0])
  row=next(r['fields'] for r in ev['candidateRows'] if r['fields']['name']=='Jessica May')
  self.assertEqual(cents(row['total'])-cents(row['pay'])-cents(row['expenses']),-500000)
 def test_every_layout_has_literal_rendered_first_and_last_row(self):
  cfg=json.loads((BASE/'reviewed-layouts.json').read_text());layouts=[l for r in cfg['reports'] for c in r['cohorts'] for l in c['layouts']]
  self.assertEqual(len(layouts),29)
  self.assertTrue(all(l['renderedEdgeChecks']['first']['name'] and l['renderedEdgeChecks']['last']['name'] for l in layouts))
if __name__=='__main__':unittest.main()
