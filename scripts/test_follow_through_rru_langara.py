#!/usr/bin/env python3
import collections,gzip,hashlib,json,pathlib,re,unittest
import follow_through_rru_langara as parser
ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED={
 'rru-2021-22':(223,25258361,273994,107,1,[-4,2]),
 'rru-2022-23':(256,29283383,893903,107,1,[8,3]),
 'rru-2024-25':(321,36566647,1301171,142,0,[-5,-1]),
 'rru-2025-26':(334,38818151,1227031,161,1,[11,5]),
 'langara-2022-23':(710,69887446,2132016,13,0,[-8,11]),
 'langara-2024-25':(950,101403151,3209876,16,0,[-11,16]),
}
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
class OriginalEmployeeSchedules(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.sources={};cls.rows={};cls.outs={}
  for kind in ['rru','langara']:
   out=ROOT/'research/salaries'/('follow-through-'+kind)
   for s in json.loads((out/'sources.json').read_text())['sources']:
    key=s['file'].removesuffix('.json.gzip')
    if key not in EXPECTED:continue
    cls.sources[key]=s;cls.rows[key]=load(out/s['file']);cls.outs[key]=out
 def test_complete_scopes_and_controls(self):
  self.assertEqual(set(self.sources),set(EXPECTED));self.assertEqual(sum(map(len,self.rows.values())),2794)
  for k,(count,pay,exp,nulls,zeros,residuals) in EXPECTED.items():
   with self.subTest(source=k):
    s=self.sources[k];r=self.rows[k]
    self.assertEqual((len(r),sum(z[3] for z in r),sum(z[4] or 0 for z in r),sum(z[4] is None for z in r),sum(z[4]==0 for z in r)),(count,pay,exp,nulls,zeros))
    self.assertEqual([z['residual'] for z in s['validation']['printedControls']],residuals)
    self.assertTrue(s['completeEmployeeSchedule']);self.assertTrue(s['retainCompiledPartition']);self.assertEqual(s['status'],'verified')
    self.assertEqual(s['validation']['physicalPagesVisuallyReviewed'],s['pages'])
    self.assertEqual(s['periodStart'],s['year'][:4]+'-04-01');self.assertEqual(s['periodEnd'],'20'+s['year'][-2:]+'-03-31')
    for z in r:
     self.assertEqual(len(z),6);self.assertIn(z[5],s['pages']);self.assertIn(',',z[1]);self.assertFalse(z[1].startswith(('Total','Schedule','<$','- ')))
 def test_all_fields_independent_readers(self):
  for k,r in self.rows.items():
   with self.subTest(source=k):
    e=load(self.outs[k]/'evidence'/f'{k}.json.gzip')
    self.assertEqual(r,e['popplerRows']);self.assertEqual(r,[z['row'] for z in e['rowReceipts']]);self.assertEqual(e['independentReaderDifferences'],[]);self.assertEqual(e['popplerUnparsed'],[])
    text1=' '.join(z['pymupdfText'] for z in e['pageText']);text2=' '.join(z['popplerLayoutText'] for z in e['pageText'])
    components=e['controlComponents'];amounts=components.get('combined',[])+components.get('belowThreshold',[])+components.get('namedEmployeeSubtotal',[])
    for a in amounts:
     self.assertIn(f'{a:,}',text1);self.assertIn(f'{a:,}',text2)
 def test_fingerprinted_deterministic_payloads(self):
  for k,s in self.sources.items():
   b=(self.outs[k]/s['file']).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),s['dataSha256']);self.assertEqual(b[4:8],b'\x00'*4)
 def test_rru_2021_22_complete_supplied_comparison(self):
  x=json.loads((self.outs['rru-2021-22']/'compiled-comparison.json').read_text());orig=sorted([z for g in x['financialGroups'] for z in g['officialOccurrences']],key=lambda z:z['rowNumber'])
  self.assertEqual(self.rows['rru-2021-22'],[z['row'] for z in orig]);self.assertEqual(x['compiledYear'],'2020/21');self.assertEqual(x['officialYear'],'2021/22');self.assertFalse(x['replacementAuthorized']);self.assertTrue(x['retainAllCompiledObservations'])
 def test_missing_blank_zero_and_clipped_title(self):
  r={z[1]:z for z in self.rows['rru-2021-22']}
  self.assertIsNone(r['Lang, Kim'][2]);self.assertEqual(r['Stewart, John'][4],0)
  for n in ['Karleen, Darryl A.','Kulikova, Nadezda','van Akker, Donna']:self.assertIsNone(r[n][4])
  self.assertTrue(r['Thomlinson, Eugene'][2].endswith('Managemen'))
 def test_multiline_titles_are_complete(self):
  r={z[1]:z for z in self.rows['rru-2024-25']}
  self.assertEqual(r['Daniels, Curtis'][2],'Manager, Reporting Applications, Integration and Data (RAID)')
  self.assertEqual(r['Gall, Leighton'][2],'Fellow, Indigenous Energy Systems Transformation, Cascade Institute')
  self.assertEqual(r['Pete, Shauneen'][2],'Indigenous Faculty and Chair, Emerging Indigenous Scholar Circle')
 def test_vertically_displaced_names_and_literal_numeric_prefix(self):
  r={z[1]:z for z in self.rows['rru-2025-26']}
  self.assertEqual(r['McDonald, Moira'][3:5],[126718,20391]);self.assertEqual(r['Hutchison, Michael'][4],0)
  self.assertEqual(r['3361 Zornes, Deborah'][3:5],[173126,7356])
 def test_all_eight_source_dispositions_are_complete(self):
  ds=[]
  for kind in ['rru','langara']:ds+=json.loads((ROOT/'research/salaries'/('follow-through-'+kind)/'dispositions.json').read_text())['sources']
  self.assertEqual(len(ds),8);self.assertEqual(sum(z['status']=='imported' for z in ds),8)
  held=[z for z in ds if z['status']=='held-for-review'];self.assertEqual(held,[])
  for z in held:self.assertEqual(z['employeeRows'],0);self.assertIsNone(z['acceptedSourceId'])
 def test_name_crops_are_individually_fingerprinted(self):
  out=ROOT/'research/salaries/follow-through-rru';r=json.loads((out/'name-crops/receipts.json').read_text())['receipts'];self.assertEqual(len(r),12)
  for z in r:
   self.assertEqual(hashlib.sha256((out/z['cropFile']).read_bytes()).hexdigest(),z['cropSha256']);self.assertEqual(hashlib.sha256((out/z['fullPageFile']).read_bytes()).hexdigest(),z['fullPageSha256']);self.assertEqual(len(z['bboxPoints']),4)
 def test_reextract_originals_when_cached(self):
  for k,c in parser.CONFIG.items():
   if c.get('scan'):continue
   p=parser.CACHE/('additional-source-'+k+'.pdf')
   if not p.exists():continue
   import fitz
   d=fitz.open(p);s=self.sources[k];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),s['sha256'])
   rows,_=parser.fitz_rows(d,c,s['employerSlug']);self.assertEqual(rows,self.rows[k])
if __name__=='__main__':unittest.main()
