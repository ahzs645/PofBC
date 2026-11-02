#!/usr/bin/env python3
import copy,decimal,gzip,hashlib,json,pathlib,unittest
import follow_through_rru_scan as scan
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/follow-through-rru'
def readgz(p):return json.loads(gzip.decompress(p.read_bytes()))
class ReviewedOriginalScan(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=next(s for s in json.loads((OUT/'sources.json').read_text())['sources'] if s['id']=='rru-sofi-2023-24-employees')
  cls.rows=readgz(OUT/cls.source['file']);cls.e=readgz(OUT/'evidence/rru-2023-24-reviewed.json.gzip');cls.raw=readgz(OUT/'evidence/rru-2023-24-dual-ocr-candidates.json.gzip');cls.d=json.loads((OUT/'scan-review/decisions.json').read_text())
 def test_complete_307_employee_rows(self):
  self.assertEqual(len(self.rows),307);self.assertEqual(self.e['pageRowCounts'],[[28,46],[29,61],[30,61],[31,61],[32,62],[33,16]])
  self.assertTrue(self.source['completeEmployeeSchedule']);self.assertTrue(self.source['retainCompiledPartition']);self.assertEqual(self.source['periodStart'],'2023-04-01');self.assertEqual(self.source['periodEnd'],'2024-03-31')
  for r in self.rows:self.assertEqual(len(r),6);self.assertEqual(r[0],'royal-roads-university');self.assertIn(',',r[1]);self.assertGreaterEqual(r[3],75000);self.assertNotIn('BOARD MEMBER',r[2])
 def test_exact_original_totals_and_source_residual(self):
  self.assertEqual(sum(decimal.Decimal(str(r[3])) for r in self.rows),decimal.Decimal('34445723.53'));self.assertEqual(sum(r[4] or 0 for r in self.rows),1106152)
  self.assertEqual([z['residual'] for z in self.e['printedControls']],[-4.47,0]);self.assertEqual(self.e['controlComponents'],{'combined':[47295027,1240360],'belowThreshold':[12849299,134208]})
  self.assertEqual(sum(r[4] is None for r in self.rows),155);self.assertEqual(sum(r[4]==0 for r in self.rows),0)
 def test_both_independent_ocr_readings_replay(self):
  schema=['employerSlug','name','position','remuneration','expenses','pdfPage']
  for kind in ['first','second']:
   original=[copy.deepcopy(z['row']) for z in self.raw[kind+'Rows']];changes=self.e[kind+'ReaderCorrections']
   for z in changes:
    i=z['rowNumber']-1;j=schema.index(z['field']);self.assertEqual(original[i][j],z['ocrValue']);original[i][j]=z['publishedValue']
   self.assertEqual(original,self.rows);self.assertEqual(original,self.e[kind+'ResolvedRows'])
  self.assertEqual(len(self.e['firstReaderCorrections']),25);self.assertEqual(len(self.e['secondReaderCorrections']),55)
 def test_original_every_row_crops(self):
  self.assertEqual(len(self.e['rowReceipts']),307);self.assertEqual([z['rowNumber'] for z in self.e['rowReceipts']],list(range(1,308)))
  for z in self.e['rowReceipts']:
   self.assertEqual(z['row'],self.rows[z['rowNumber']-1]);self.assertTrue(z['sourceCellsVisuallyReviewed']);self.assertEqual(hashlib.sha256((OUT/z['cropFile']).read_bytes()).hexdigest(),z['cropSha256']);self.assertEqual(len(z['bboxPoints']),4);self.assertTrue((OUT/z['sourceSheet']).exists())
 def test_source_exceptions_preserved(self):
  r={z[1]:z for z in self.rows}
  self.assertEqual(r['CORAK, LISA'][3],75928.53);self.assertEqual(r['LITTLER, BLAIR'][3],198716);self.assertIn('DU, JUAN',r)
  self.assertTrue(r['PETE, SHAUNEEN'][2].endswith('EMERGING INDIGENOUS'))
  self.assertIsNone(r['WHITE, RHONDA'][4]);self.assertIsNone(r['XU, YANMIN'][4]);self.assertEqual(r['SHEARER, KARLA'][3],75929);self.assertEqual(r['SHEFFIELD, STEPHANIE'][3],75929)
 def test_unanimous_ocr_errors_also_reviewed(self):
  self.assertEqual(self.raw['firstRows'][56]['row'][4],307);self.assertEqual(self.raw['secondRows'][56]['row'][4],307);self.assertEqual(self.rows[56][4],907)
  self.assertEqual(self.rows[245][3],75929);self.assertNotEqual(self.raw['firstRows'][245]['row'][3],75929);self.assertNotEqual(self.raw['secondRows'][245]['row'][3],75929)
 def test_fingerprints_bind_review(self):
  self.assertEqual(self.d['pdfSha256'],self.source['sha256']);self.assertEqual(self.d['candidateDataSha256'],hashlib.sha256((OUT/'evidence/rru-2023-24-dual-ocr-candidates.json.gzip').read_bytes()).hexdigest());self.assertEqual(self.source['dataSha256'],hashlib.sha256((OUT/self.source['file']).read_bytes()).hexdigest())
  self.assertEqual(self.d['unresolvedCells'],[]);self.assertEqual(self.e['unresolvedCells'],[])
 def test_full_visual_scope_and_controls(self):
  v=json.loads((OUT/'visual/rru-2023-24.json').read_text());self.assertEqual(v['status'],'reviewed');self.assertEqual(v['reviewedRows'],307);self.assertEqual(len(v['reviewedSheets']),16)
  for z in v['reviewedSheets']+v['controlCrops']:self.assertEqual(hashlib.sha256((OUT/z['file']).read_bytes()).hexdigest(),z['sha256'])
 def test_native_reader_limitation_is_explicit(self):
  self.assertIn('No employee cells',self.e['nativeOriginalReaders']['PyMuPDF']);self.assertIn('No employee cells',self.e['nativeOriginalReaders']['Poppler']);self.assertEqual(len(self.e['independentReaders']),3)
 def test_cached_ocr_reextracts_identically(self):
  if not (scan.CACHE/'rru-2023-24-e2-p33-expenses.tsv').exists():self.skipTest('Original OCR cache unavailable')
  for engine,key in [(1,'firstRows'),(2,'secondRows')]:self.assertEqual([z for n in scan.PAGES for z in scan.extract(n,engine)],self.raw[key])
if __name__=='__main__':unittest.main()
