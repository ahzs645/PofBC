#!/usr/bin/env python3
"""Real-source regressions for the eight north school OCR schedules."""
import collections,gzip,json,unittest
from decimal import Decimal
from pathlib import Path
from gap_school_north_parse import AREA,ROOT,DEFS,FIELD_NAMES,money,parse,signature,words
from gap_school_north_pixels import classify

def read(path):
 raw=Path(path).read_bytes()
 return json.loads(gzip.decompress(raw) if str(path).endswith('.gzip') else raw)

class SchoolNorthSourceTests(unittest.TestCase):
 def test_actual_row_scope_and_multiplicity(self):
  expected={8:(9,345),28:(7,210),54:(7,127),58:(7,153),59:(7,248),60:(7,397),81:(5,50),82:(8,297)}
  for n,counts in expected.items():
   proof=read(AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip');a,b=proof['finalReaders'].values()
   self.assertEqual([signature(x) for x in a],[signature(x) for x in b],n)
   self.assertEqual(tuple(sum(x['category']==cat for x in a) for cat in ['school-trustees','employee-remuneration']),counts,n)
   self.assertFalse(any(str(x['name']).lower().startswith(('total','whose remuneration','paid to each')) for x in a))
  self.assertEqual(sum(sum(x) for x in expected.values()),1884)

 def test_wrapped_aggregate_never_becomes_person(self):
  for n,page in [(54,51),(59,59)]:
   raw=read(AREA/'raw-ocr'/f'sd{n:02}-p{page:03}.json.gzip')
   self.assertTrue(any('WHOSE' in w['text'].upper() for w in words(raw,'tesseract')))
   for engine in ['tesseract','rapid']:
    self.assertFalse(any('WHOSEREMUNERATION' in ''.join(r['name'].upper().split()) for r in parse(raw,n,engine)))

 def test_sd59_trustees_are_not_employee_column_layout(self):
  raw=read(AREA/'raw-ocr'/'sd59-p053.json.gzip')
  for engine in ['tesseract','rapid']:
   rows=parse(raw,59,engine);self.assertEqual(len(rows),7)
   self.assertEqual({r['category'] for r in rows},{'school-trustees'})
   self.assertEqual(''.join(rows[0]['name'].split()),'ANDERSON,CHAD')
   if engine=='tesseract':self.assertEqual(sum(Decimal(r['remuneration']) for r in rows),Decimal('125569.44'))

 def test_qs_alternative_tesseract_geometry_keeps_complete_grid(self):
  proof=read(AREA/'sd28-image-reviewed-candidate.json.gzip')
  rows=proof['finalReaders']['tesseract'];self.assertEqual(len(rows),217)
  self.assertEqual(rows[6]['remuneration'],'17733.32')
  self.assertEqual(rows[96]['name'],'HYDAMACKA, REBECCA')
  self.assertEqual(rows[96]['remuneration'],'88812.97');self.assertIsNone(rows[96]['expenses'])

 def test_literal_source_typo_clipped_titles_and_capitals(self):
  rows=read(AREA/'sd82-image-reviewed-candidate.json.gzip')['finalReaders']['tesseract']
  self.assertEqual(rows[10]['position'],'Teahcers (Terrace)')
  self.assertEqual(rows[7]['name'],'Warcup, Margaret')
  self.assertEqual(rows[117]['name'],'Giguere, Tina')
  self.assertEqual(rows[185]['name'],'Maier, Marlene Laura')
  self.assertTrue(any(x['position']=='CUPE 2052 12 MONTH (' for x in rows))
  self.assertTrue(any(x['position']=='ADMINISTRATIVE OFFIC' for x in rows))

 def test_name_word_boundaries_cannot_be_hidden_as_layout_whitespace(self):
  a={'name':'Denton, JenniferA','position':'TEACHERS','remuneration':'1.00','expenses':None,'pdfPage':50,'category':'employee-remuneration'}
  b=dict(a,name='Denton, Jennifer A');self.assertNotEqual(signature(a),signature(b))
  self.assertEqual(signature(dict(a,name='Denton,Jennifer A')),signature(b))
  for n,seq,name in [(28,147,'MONSOUR, DERYCK E A'),(58,30,'Cleaveley, Aaron C A'),(58,37,'Denton, Jennifer A'),(58,80,'Livesey, Merrill A'),(82,187,'Maltais, Marie-Philippe'),(82,189,'Marshall, Shylah')]:
   self.assertEqual(read(AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip')['finalReaders']['tesseract'][seq-1]['name'],name)

 def test_exact_two_damaged_names_do_not_lose_payments_or_guess_identity(self):
  for n in DEFS:
   p=read(AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip');rows=p['finalReaders']['tesseract']
   nulls=[(i,r['position'],r['remuneration'],r['expenses']) for i,r in enumerate(rows,1) if r['name'] is None]
   expected=[(60,'TEACHERS','87804.23','0.00'),(128,'TEACHERS','103044.97','0.00')] if n==58 else []
   self.assertEqual(nulls,expected)
  p=read(AREA/'sd58-image-reviewed-candidate.json.gzip')
  self.assertEqual([x['visibleFragment'] for x in read(AREA/'own-image-review.json')['sources']['58']['unresolvedSourceFields']],['Hodd?r, Allison','Sigur?sson, Lara'])

 def test_source_literal_zero_is_not_dash_or_missing(self):
  rows=read(AREA/'sd58-image-reviewed-candidate.json.gzip')['finalReaders']['tesseract']
  self.assertEqual(sum(r['expenses']=='0.00' for r in rows),65)
  self.assertEqual(money('0.00','cents'),('0.00',''))
  self.assertEqual(money('-','cents'),(None,''))
  self.assertTrue(money('','cents')[0].startswith('UNRESOLVED:'))
  self.assertEqual(money('-1,234.50','cents'),('-1234.50',''))
  self.assertTrue(money('12.3','cents')[0].startswith('UNRESOLVED:'))

 def test_pixels_do_not_auto_erase_detected_numeric_expenses(self):
  checks=read(AREA/'original-expense-cell-pixels.json.gzip')['rows']
  numeric=[r for r in checks if r['preferredParsedExpense'] is not None and not str(r['preferredParsedExpense']).startswith('UNRESOLVED:')]
  self.assertGreater(len(numeric),200)
  self.assertFalse([r for r in numeric if r['classification']!='other-source-ink-requires-review'])
  self.assertEqual(classify(40,20,bytes([255])*800)['classification'],'visibly-empty-source-cell')

 def test_personal_image_amendment_retains_raw_unparsed_positive_expense(self):
  before=read(AREA/'sd60-pixel-candidate.json.gzip')['readers']['tesseract'][122]
  after=read(AREA/'sd60-image-reviewed-candidate.json.gzip')['finalReaders']['tesseract'][122]
  self.assertEqual(before['rawMoneyCells'][1],'67.79_')
  self.assertEqual(after['expenses'],'67.79');self.assertEqual(after['remuneration'],'79156.17')

 def test_no_accepted_same_period_baseline_was_displaced(self):
  baseline=read(AREA.parent/'baseline.json.gzip')
  for n in DEFS:
   slug=f'school-district-{n:02}'
   self.assertFalse([g for g in baseline['groups'] if g['employerSlug']==slug and g['year']=='2024/25'])

 def test_all_candidate_cohorts_retain_compiled_partitions(self):
  sources=read(ROOT/'research/salaries/gap-fill-school-north/sources.json')['sources']
  self.assertEqual(len(sources),16)
  for source in sources:
   self.assertTrue(source['validation']['compiledPartitionRetained'])
   self.assertTrue(source['validation']['compiledPartitionRetentionReason'])
   self.assertEqual(source['year'],'2024/25')
   self.assertEqual(source['rowCount'],len(read(ROOT/'research/salaries/gap-fill-school-north'/source['file'])))

if __name__=='__main__':unittest.main()
