#!/usr/bin/env python3
import copy,gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import continue_municipal as m

class MunicipalContinuationTests(unittest.TestCase):
 def setUp(self):
  self.part={'columns':{'name':[0,30],'position':[30,65],'pay':[65,85],'expenses':[85,110]},'y':[0,40],'rowCount':2,'maxRowDistance':6,'corrections':[]}
  self.words=[[0,8,20,12,'A, J.'],[32,8,60,12,'Chief'],[32,12,60,16,'Officer'],[68,8,82,12,'100.50'],[88,8,108,12,'-'],[0,28,20,32,'B, K.'],[32,28,60,32,'Clerk'],[68,28,82,32,'90.00'],[88,28,108,32,'0.00']]
 def test_missing_and_explicit_zero_expenses_remain_distinct(self):
  rows=m.extract(self.words,self.part);self.assertIsNone(rows[0]['expenses']);self.assertEqual(rows[1]['expenses'],0);self.assertEqual(rows[0]['name'],'A, J.')
 def test_wrapped_title_keeps_line_order(self):
  self.assertEqual(m.extract(self.words,self.part)[0]['position'],'Chief Officer')
 def test_money_definition_rejects_expense_inclusive_text(self):
  for value in ['', '-', '–', '—', '‐']:self.assertIsNone(m.money(value))
  self.assertEqual(m.money('-309'),-30900)
  with self.assertRaises(ValueError):m.money('100 plus expenses 20')
 def test_row_boundary_ambiguity_is_held(self):
  with self.assertRaisesRegex(ValueError,'Ambiguous row boundary'):m.extract(self.words+[[32,18,55,22,'ambiguous']],self.part)
 def test_expected_row_count_guards_multiplicity(self):
  part=copy.deepcopy(self.part);part['rowCount']=1
  with self.assertRaisesRegex(ValueError,'salary anchors'):m.extract(self.words,part)
 def test_reviewed_correction_requires_original_context(self):
  part=copy.deepcopy(self.part);part['corrections']=[{'row':0,'field':'name','before':'wrong raw original','after':'Invented'}]
  with self.assertRaisesRegex(ValueError,'correction changed'):m.extract(self.words,part)
 def test_clipped_word_exemption_is_exact_and_local(self):
  part=copy.deepcopy(self.part);part['ignoredClippedWords']=[{'text':'hidden','x':67,'y':8,'tolerance':.1}]
  self.assertEqual(m.extract(self.words+[[67,8,80,12,'hidden']],part)[0]['pay'],10050)
  with self.assertRaises(ValueError):m.extract(self.words+[[69,8,82,12,'hidden']],part)
 def test_complete_offline_evidence_replay_needs_no_pdf_or_ocr(self):
  cfg=json.loads((m.OUT/'reviewed-layouts.json').read_text())
  with patch.object(m.fitz,'open',side_effect=AssertionError('Offline replay opened PDF')),patch.object(m.subprocess,'check_output',side_effect=AssertionError('Offline replay launched external engine')):
   m.build(cfg,Path('/not-used'),check_data=True)
 def test_accepted_scopes_do_not_use_inclusive_totals_or_conflicted_staff_year(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  for s in sources:
   if s['employerSlug']=='district-of-wells':self.assertEqual(s['category'],'elected-officials')
   if s['employerSlug']=='district-of-port-edward':self.assertEqual(s['category'],'elected-officials')
  s=next(s for s in sources if s['employerSlug']=='district-of-port-edward'and s['year']=='2025')
  row=json.loads(gzip.decompress((m.OUT/s['file']).read_bytes()))[0]
  self.assertEqual(row[3:5],[21543,23328]);self.assertNotEqual(row[3],44871)
 def test_fraser_lake_explicit_zero_and_metchosin_unpublished_expense(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  for slug,name,expected in [('village-of-fraser-lake','Campbell, Cameron',0),('district-of-metchosin','Dunlop, S',None)]:
   source=next(s for s in sources if s['employerSlug']==slug and s['category']=='employee-remuneration')
   rows=json.loads(gzip.decompress((m.OUT/source['file']).read_bytes()));self.assertEqual(next(r for r in rows if r[1]==name)[4],expected)


 def test_overlay_original_spacing_and_initials_are_guarded(self):
  sources=json.loads((m.OUT/'sources.json').read_text())['sources']
  source=next(s for s in sources if s['employerSlug']=='district-of-elkford'and s['category']=='employee-remuneration')
  names=[r[1]for r in json.loads(gzip.decompress((m.OUT/source['file']).read_bytes()))]
  for name in ['Dawson, C','Gagnon, M','Madsen, T','Rookes, M','Kliment,E']:self.assertIn(name,names)
  proof=json.loads(gzip.decompress((m.OUT/source['validation']['evidenceFile']).read_bytes()))
  self.assertEqual(proof['manualReviewCorrections'],source['validation']['corrections'])
 def test_manual_scan_fixture_cannot_change_during_offline_replay(self):
  cfg=json.loads((m.OUT/'reviewed-layouts.json').read_text());report=next(r for r in cfg['reports']if r['sourceKind']=='official-scanned-pdf');report['sections'][0]['manualRows'][0]['pay']+=1
  with self.assertRaisesRegex(ValueError,'manual scan transcript changed'):m.build(cfg,Path('/unused'),check_data=True)
 def test_acquisition_queue_has_exact_schema_and_valid_routes(self):
  path=m.ROOT/'research/salaries/continuation-2026-11-01/municipal/work-queue.json'
  keys={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
  queue=json.loads(path.read_text());self.assertEqual(len(queue),len({t['id']for t in queue}))
  for task in queue:
   self.assertEqual(set(task),keys);self.assertIn(task['route'],{'processing','public-archive-research','ordinary-records-request','clarification-request','foi-fallback'});self.assertIsInstance(task['reportingPeriods'],list)

if __name__=='__main__':unittest.main()
