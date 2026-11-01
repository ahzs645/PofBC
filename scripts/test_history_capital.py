#!/usr/bin/env python3
"""Historical source-fidelity regressions; no network needed."""
import copy,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from parse_history_capital import BASE,money,cents,extract,read_table
class HistoryCapitalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.manifest=json.loads((BASE/'sources.json').read_text());cls.cfg=json.loads((BASE/'reviewed-layouts.json').read_text())
 def source(self,slug,year,category):return next(s for s in self.manifest['sources'] if (s['employerSlug'],s['year'],s['category'])==(slug,year,category))
 def evidence(self,s):return json.loads(gzip.decompress((BASE/s['validation']['evidenceFile']).read_bytes()))
 def test_money_preserves_missing_zero_cents_and_negatives(self):
  for t in ['','-','‐','–','—']:self.assertIsNone(money(t))
  self.assertEqual(money('0.00'),0);self.assertEqual(money('(1,234.56)'),-1234.56);self.assertEqual(money('-2.50'),-2.5)
  self.assertEqual(cents(money('87,435.71')),8743571)
  with self.assertRaises(ValueError):money('75,OOO')
 def test_changed_original_fails_before_table_processing(self):
  with tempfile.NamedTemporaryFile() as f:
   f.write(b'%PDF changed');f.flush()
   with self.assertRaisesRegex(ValueError,'Original hash changed'):extract(self.cfg['reports'][0],Path(f.name))
 def test_every_published_field_matches_both_independent_readers(self):
  self.assertEqual(len(self.manifest['sources']),34);self.assertEqual(sum(s['rowCount'] for s in self.manifest['sources']),797)
  for s in self.manifest['sources']:
   ev=self.evidence(s);raw=(BASE/s['file']).read_bytes();rows=json.loads(gzip.decompress(raw));self.assertEqual(hashlib.sha256(raw).hexdigest(),s['dataSha256'])
   self.assertEqual(len(rows),s['rowCount'])
   for r,e in zip(rows,ev['rows']):
    if 'pymupdf' in e:self.assertEqual(e['pymupdf']['values'],e['poppler']['values'])
    else:self.assertTrue(e['newOcrAllFieldsCorroboratedAfterAdjudication'])
    self.assertEqual(r[1:5],[e['fields']['name'],e['fields'].get('position'),e['fields']['pay'],e['fields'].get('expenses')])
 def test_no_scanned_schedule_is_mislabelled_native(self):
  self.assertEqual(sum(s['validation']['nativeTablePagesVerified'] for s in self.manifest['sources']),32)
  self.assertTrue(all(s['validation']['ocrReview'] and s['validation']['allOcrDisagreementsAdjudicated'] for s in self.manifest['sources'] if not s['validation']['nativeTablePagesVerified']))
  self.assertEqual({s['employerSlug'] for s in self.manifest['sources']},{'town-of-ladysmith','city-of-langford','district-of-north-saanich','town-of-sidney','city-of-colwood','district-of-oak-bay'})
 def test_every_layout_pins_literal_rendered_first_and_last_rows(self):
  ls=[l for s in self.cfg['reports'] for c in s['cohorts'] for l in c['layouts']];self.assertEqual(len(ls),42)
  self.assertTrue(all(l['renderedEdgeChecks']['first']['name'] and l['renderedEdgeChecks']['last']['name'] for l in ls))
 def test_summary_text_cannot_join_final_job_title(self):
  s=self.source('city-of-langford','2021','employee-remuneration');ev=self.evidence(s);layout=ev['layout']['layouts'][-1]
  words=[w for e in ev['rows'] if e['page']==8 for w in e['pymupdf']['words']];last=ev['rows'][-1]['pymupdf']['anchorY'];words.append({'x':190,'y':last+.1,'right':250,'bottom':last+7,'t':'Consolidated'})
  with self.assertRaisesRegex(ValueError,'Rendered source edge changed'):read_table(words,layout)
 def test_currency_marker_cannot_join_text(self):
  for s in self.manifest['sources']:
   for e in self.evidence(s)['rows']:
    self.assertNotIn('$',e['fields']['name']);self.assertNotIn('$',e['fields'].get('position') or '')
 def test_legitimate_initial_A_is_preserved(self):
  s=self.source('district-of-north-saanich','2023','employee-remuneration');rows=self.evidence(s)['rows'];self.assertIn('Duff, A',[r['fields']['name'] for r in rows]);self.assertIn('Elia, A',[r['fields']['name'] for r in rows])
 def test_same_published_name_with_distinct_jobs_is_not_deduplicated(self):
  s=self.source('district-of-north-saanich','2023','employee-remuneration');rs=[e['fields'] for e in self.evidence(s)['rows'] if e['fields']['name']=='Munro, S'];self.assertEqual(len(rs),2);self.assertEqual({r['position'] for r in rs},{'GIS Technician','Chief Administrative Officer'})
 def test_unknown_expenses_do_not_become_zero(self):
  s=self.source('city-of-langford','2021','elected-officials');ev=self.evidence(s)
  self.assertTrue(all(r['fields']['expenses'] is None for r in ev['rows']));self.assertIsNone(s['validation']['printedControls'][1]['printedControl']);self.assertIsNone(s['validation']['printedControls'][1]['residual']);self.assertEqual(s['validation']['knownNumericExpenseRows'],0);self.assertIn('does not establish nil',s['publicWarning'])
 def test_published_remuneration_total_does_not_require_missing_component_zero(self):
  s=self.source('town-of-sidney','2024','elected-officials');r=self.evidence(s)['rows'][0]['fields'];self.assertIsNone(r['benefits']);self.assertEqual(r['gross'],45122);self.assertEqual(r['pay'],45122)
 def test_missing_printed_comparator_remains_null(self):
  for s in self.manifest['sources']:
   if s['employerSlug']=='town-of-sidney' and s['category']=='employee-remuneration':self.assertIsNone(s['thresholdComparison'])
 def test_faithful_residuals_are_explicit_without_inferred_cause(self):
  ss=[s for s in self.manifest['sources'] if any(c['residual'] for c in s['validation']['printedControls'])];self.assertEqual(len(ss),17)
  self.assertTrue(all('cause is unresolved' in s['publicWarning'] for s in ss))
  s=self.source('town-of-ladysmith','2022','employee-remuneration');self.assertEqual(s['validation']['printedControls'][1]['residual'],5)
 def test_aggregate_control_conflict_is_preserved(self):
  s=self.source('town-of-sidney','2022','elected-officials');eq=s['validation']['controlEquations'];self.assertEqual([e['actualResidual'] for e in eq],[-1,1]);self.assertIn('exceeds printed gross',s['publicWarning'])
 def test_no_printed_control_is_not_an_invented_zero(self):
  s=self.source('city-of-colwood','2012','elected-officials');self.assertTrue(all(c['printedControl'] is None and c['residual'] is None for c in s['validation']['printedControls']));self.assertIn('publishes no group subtotal',s['publicWarning'])
  s=self.source('city-of-colwood','2012','employee-remuneration');self.assertEqual(s['validation']['printedControls'][0]['residual'],-47.55);self.assertIsNone(s['validation']['printedControls'][1]['printedControl'])
 def test_explicit_total_survives_blank_benefit_and_preserves_source_equations(self):
  s=self.source('city-of-colwood','2016','employee-remuneration');r=next(e['fields'] for e in self.evidence(s)['rows'] if e['fields']['name']=='CARLSEN, DENNIS');self.assertIsNone(r['benefits']);self.assertEqual(r['pay'],76875.21)
  s=self.source('city-of-colwood','2021','employee-remuneration');self.assertEqual(len(s['validation']['componentResiduals']),13);self.assertIn('cause is unresolved',s['publicWarning'])
 def test_ocr_errors_are_adjudicated_and_original_spelling_retained(self):
  s=self.source('city-of-langford','2010','employee-remuneration');rs=self.evidence(s)['rows'];r=next(e for e in rs if e['fields']['name']=='Mahovlich, Michelle');self.assertEqual(r['fields']['pay'],104148.46);self.assertIn('404,148.46',r['tesseractRawLine']);self.assertIn('404,148.46',r['adjudication']['ocrNumericCorrections'])
  f=next(e for e in rs if e['fields']['name']=='Fletcher, Lorne');self.assertIn('Fletcher, Lome',f['tesseractRawLine']);self.assertIn('Both retained machine readings say Lome',f['adjudication']['reason'])
  self.assertIn('Barber, Jennfier',[e['fields']['name'] for e in rs]);self.assertNotIn('Barber, Jennifer',[e['fields']['name'] for e in rs])
 def test_oak_bay_keeps_departments_and_explicit_zero_without_inventing_names(self):
  s=self.source('district-of-oak-bay','2024','employee-remuneration');ev=self.evidence(s);self.assertEqual(len(ev['rows']),98)
  r=next(e['fields'] for e in ev['rows'] if e['fields']['name']=='Young Cameron');self.assertEqual(r['expenses'],0);self.assertEqual(r['department'],'Fire');self.assertEqual(r['position'],'Fire Fighter')
  r=next(e['fields'] for e in ev['rows'] if e['fields']['name']=='Laktin Marilyn');self.assertEqual(r['department'],'Finance, IT & Asset Management');self.assertEqual(r['position'],'Manager Financial Operations')
 def test_oak_bay_council_is_held_without_blocking_employee_cohort(self):
  self.assertFalse(any(s['employerSlug']=='district-of-oak-bay' and s['category']=='elected-officials' for s in self.manifest['sources']))
  ev=json.loads(gzip.decompress((BASE/'evidence/district-of-oak-bay-2024-elected-officials-held.json.gzip').read_bytes()));self.assertEqual(ev['individualRowsAccepted'],0);self.assertEqual(ev['residuals'],[2,-270]);r=next(e['fields'] for e in ev['candidateRows'] if e['fields']['name']=='Watson, Lesley');self.assertEqual(cents(r['total'])-cents(r['pay'])-cents(r['expenses']),-325600)
 def test_hidden_oak_bay_artifact_is_source_specific_and_does_not_filter_letters(self):
  s=self.source('district-of-oak-bay','2024','employee-remuneration');ev=self.evidence(s);layout=ev['layout']['layouts'][1];self.assertEqual(layout['excludedTextArtifacts'][0]['text'],'3.5')
  self.assertEqual(next(e['fields']['position'] for e in ev['rows'] if e['fields']['name']=='Laktin Marilyn'),'Manager Financial Operations')
  self.assertEqual(layout['excludedTextArtifacts'][0]['expectedWordCount'],1)
 def test_category_period_keys_unique_and_full_named_cohorts(self):
  keys=[(s['employerSlug'],s['year'],s['category']) for s in self.manifest['sources']];self.assertEqual(len(keys),len(set(keys)));self.assertTrue(all(s['completeForNamedPopulation'] and not s['partialImport'] for s in self.manifest['sources']))
if __name__=='__main__':unittest.main()
