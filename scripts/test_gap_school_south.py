"""Offline source-fixture regressions for southern school extraction decisions."""
import gzip,hashlib,json,re,unittest
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA,ROOT
from gap_school_south_dash import describe_mask,is_source_dash
from gap_school_south_scan import SPECS,tesseract,paddle,amount
from gap_school_south_native import money
from gap_school_south_finalize_scans import requires_personal_source_receipt

def load(path):return json.loads(gzip.decompress(path.read_bytes()))
def mask(s):return [[c=='#' for c in row] for row in s.splitlines()]

class SouthernSourceRegressions(unittest.TestCase):
 def test_blank_zero_and_multiple_marks_are_not_a_source_dash(self):
  cal={'widthRange':[5,13],'heightRange':[1,5],'minimumAspectRatio':1.6,'minimumInkFill':.45}
  self.assertFalse(is_source_dash(describe_mask(mask('........\n........')),cal))
  self.assertFalse(is_source_dash(describe_mask(mask('..###...\n.#...#..\n.#...#..\n..###...')),cal))
  self.assertFalse(is_source_dash(describe_mask(mask('#####...#####')),cal))
  self.assertTrue(is_source_dash(describe_mask(mask('.#######.\n.#######.')),cal))
 def test_published_dash_is_unresolved_until_source_ink_proof(self):
  self.assertEqual(amount('-'),'UNRESOLVED:source-dash-needs-pixel-proof')
  self.assertEqual(amount(''),'UNRESOLVED:missing-detection')
  self.assertEqual(amount('0.00'),'0.00')
  self.assertEqual(amount('(94.00)'),'-94.00')
  self.assertEqual(money('(94)'),'-94')
 def test_actual_expense_glyph_benchmark_shapes_reject_numeric_cells(self):
  packet=json.loads((AREA/'expense-dash-source-benchmark-packet.json').read_text());cal=json.loads((AREA/'expense-dash-primary-calibration.json').read_text())['calibrations']
  for n in [35,38,69,70]:
   xs=[x for x in packet['sourceOnlyImageTargets'] if x['district']==n]
   self.assertEqual(len(xs),15)
   self.assertTrue(all(is_source_dash(x['geometry'],cal[str(n)]) for x in xs[:10]))
   self.assertFalse(any(is_source_dash(x['geometry'],cal[str(n)]) for x in xs[10:]))
 def test_all_committed_raw_scan_rows_replay_both_independent_parsers(self):
  for n in [35,38,69,70,78,79]:
   d=load(AREA/f'sd{n}-scan-parsed-v9.json.gzip');first=[];second=[]
   for p in SPECS[n]['pages']:
    raw=load(AREA/'raw-ocr'/f'sd{n}-sofi-2025-p{p}.json.gzip');first+=tesseract(raw,n);second+=paddle(raw,n)
   self.assertEqual(first,d['tesseractRows']);self.assertEqual(second,d['paddleRows'])
 def test_whole_page_census_recovers_six_real_payment_rows(self):
  expected={78:{'Hoshowski, Douglas':'127401.92','Moorthy, Shalegh':'112427.35','Mossey, Jenny M':'111111.92','Urquhart, Hannah':'93892.67'},79:{'Barber, Jennifer':'98418.60','Cameron, Wayne':'86297.50'}}
  for n,lookups in expected.items():
   d=load(AREA/f'sd{n}-scan-reviewed-candidate-v14.json.gzip');xs=[r for r in d['rows'] if r['legacySequenceV6'] is None];self.assertEqual({r['name']:r['remuneration'] for r in xs},lookups)
 def test_source_name_and_money_corrections_are_literal(self):
  d=load(AREA/'sd78-scan-reviewed-candidate-v14.json.gzip');r=next(r for r in d['rows'] if r['name']=='Parsons, David S');self.assertEqual(r['remuneration'],'111122.78');self.assertEqual(r['expenses'],'0.00')
  d=load(AREA/'sd35-scan-reviewed-candidate-v14.json.gzip');r=next(r for r in d['rows'] if r['name']=='TREDGETT, BRANDI');self.assertEqual(r['expenses'],'52')
  d=load(AREA/'sd38-scan-reviewed-candidate-v14.json.gzip');self.assertTrue(any(r['name']=='KOZIJ, K' for r in d['rows']));self.assertTrue(any(r['name']=='FUJITA, R' and r['position']=='TEACHER' for r in d['rows']))
 def test_compensation_footnote_is_not_part_of_person_name(self):
  d=load(AREA/'sd79-scan-reviewed-candidate-v14.json.gzip');r=next(r for r in d['rows'] if r['name']=='Low, Ian');self.assertEqual(r['sourceNameFootnote'],'**');self.assertEqual(r['expenses'],'6386.27');self.assertEqual(r['remuneration'],'112828.44')
 def test_repeated_trustee_observations_are_not_deleted(self):
  d=load(AREA/'sd38-scan-reviewed-candidate-v14.json.gzip');xs=[r for r in d['rows'] if r['category']=='school-trustees'];self.assertEqual(len(xs),10)
  self.assertEqual(sum(r['name']=='HAMAGUCHI, K' for r in xs),2)
  self.assertEqual(sum(r['name']=='LARSON, H' for r in xs),2)
  self.assertEqual(sum(r['name']=='YANG, Z' for r in xs),2)
 def test_unknown_delta_name_retains_visible_fragment_and_payment(self):
  d=load(AREA/'sd37-selected-candidate-v5.json.gzip');r=d['rows'][925];self.assertIsNone(r['name']);self.assertEqual(r['sourceVisibleNameFragment'],'STEWART-HIBBELN, BRIANN');self.assertEqual(r['position'],'TEACHER');self.assertEqual(r['remuneration'],'90486');self.assertEqual(r['expenses'],'42')
 def test_controls_are_literal_not_force_balanced(self):
  expected={35:('166850947','902007'),38:('167465154','1018508'),69:('32130920.92','164942.12'),70:('30296137.71','252872.22'),78:('15064017.60','155972.29'),79:('57938687.24','881200.55')}
  for n,total in expected.items():
   d=load(AREA/f'sd{n}-scan-reviewed-candidate-v14.json.gzip');self.assertFalse(d['remainingFlags']);xs=[r for r in d['rows'] if r['category']=='employee-remuneration'];actual=tuple(str(sum((Decimal(r[f]) for r in xs if r[f] is not None),Decimal(0))) for f in ['remuneration','expenses']);self.assertEqual(actual,total)
  self.assertNotEqual(expected[35],('166850934','902000'));self.assertNotEqual(expected[38],('167465170','1018479'))
 def test_two_numeric_sevens_cannot_override_actual_source_dashes(self):
  d=load(AREA/'sd35-scan-reviewed-candidate-v14.json.gzip');raw=load(AREA/'sd35-scan-parsed-v9.json.gzip')
  for seq in [498,523]:
   self.assertEqual(raw['tesseractRows'][seq-1]['expenses'],'7');self.assertIsNone(d['rows'][seq-1]['expenses'])
 def test_low_model_scores_require_a_personal_source_receipt(self):
  raw=load(AREA/'sd35-scan-parsed-v9.json.gzip');one=raw['tesseractRows'][940];two=raw['paddleRows'][940]
  self.assertTrue(requires_personal_source_receipt(one,two,False));self.assertFalse(requires_personal_source_receipt(one,two,True))
 def test_normalized_collection_and_evidence_fingerprints(self):
  collection=ROOT/'research/salaries/gap-fill-school-south';d=json.loads((collection/'sources.json').read_text());self.assertEqual(len(d['sources']),20);self.assertTrue(d['reviewed']);self.assertEqual(sum(s['rowCount'] for s in d['sources']),9845)
  for s in d['sources']:
   data=(collection/s['file']).read_bytes();raw=gzip.decompress(data);rows=json.loads(raw);evidence=(collection/s['provenanceFile']).read_bytes()
   self.assertEqual(hashlib.sha256(data).hexdigest(),s['dataSha256']);self.assertEqual(hashlib.sha256(raw).hexdigest(),s['normalizedSha256']);self.assertEqual(hashlib.sha256(evidence).hexdigest(),s['provenanceSha256']);self.assertEqual(len(rows),s['rowCount']);self.assertTrue(all(len(r)==6 and r[0]==s['employerSlug'] for r in rows));self.assertEqual(s['year'],'2024/25');self.assertEqual(s['status'],'verified');self.assertTrue(s['validation']['compiledPartitionRetained'])
 def test_no_cross_period_or_identity_inference(self):
  d=load(AREA/'sd37-selected-candidate-v5.json.gzip');self.assertEqual(d['source']['sha256'],'1a4a0667cbfa4e90f3a73ea4446dfe2f25ad79a0de07ac0f623e43a7a2a92c51');self.assertEqual(d['controls']['employee-remuneration']['residuals'],['2','-5']);self.assertTrue(d['noOutreach'])

if __name__=='__main__':unittest.main()
