import gzip,importlib.util,json,re,subprocess,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('early',Path(__file__).resolve().parents[1]/'scripts/import-provincial-early.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class EarlyTest(unittest.TestCase):
 def test_counts_and_no_overlap(self):
  sources=json.loads((p.BASE/'sources.json').read_text())['sources'];self.assertEqual(len(sources),14)
  self.assertEqual(sum(s['rowCount'] for s in sources if s['category']=='deputy-minister-remuneration'),310)
  self.assertEqual(sum(s['rowCount'] for s in sources if s['category']=='minister-executive-salary'),242)
  self.assertTrue(all(s['periodEnd']<='2006-03-31' for s in sources))
 def test_reproduce_from_pdf_and_controls(self):
  sources=json.loads((p.BASE/'sources.json').read_text())['sources']
  for label in p.CONFIG:
   original=p.BASE/'originals'/(label+'.pdf');records,_=p.parse(subprocess.check_output(['pdftotext','-layout',str(original),'-']).decode(),label)
   for kind,rows in records.items():
    s=next(s for s in sources if s['id']=='provincial-early-'+label+'-'+kind);data=(p.BASE/s['file']).read_bytes()
    self.assertEqual(p.sha(original.read_bytes()),s['sha256']);self.assertEqual(p.sha(data),s['dataSha256']);self.assertEqual(p.normalize(rows,kind,label),json.loads(gzip.decompress(data)))
    self.assertEqual(sum(r[3] for r in json.loads(gzip.decompress(data))),s['totalRemuneration'])
    for i,v in enumerate(s['validation']['publishedColumnTotals']):
     if v is not None:self.assertEqual(sum(r['amounts'][i] or 0 for r in rows)-v,s['validation']['publishedTotalDeltas'][i])
 def test_2003_discrepancies_independently_confirmed(self):
  raw=subprocess.check_output(['pdftotext','-f','9','-l','9','-raw',str(p.BASE/'originals/2003-04.pdf'),'-']).decode();audit=json.loads((p.BASE/'2003-04.audit.json').read_text());n=0
  for rows in audit.values():
   for r in rows:
    m=re.search(re.escape(r['name'])+r'(?:[45])?\s+((?:\d[\d,]*\s+)+)',raw);self.assertIsNotNone(m,r['name']);nums=[int(v.replace(',','')) for v in m[1].split()]
    if nums[0]==5 and r['name']=='CAMPBELL, D SCOTT':nums=nums[1:]
    expected=[v for v in r['amounts'] if v is not None];self.assertEqual(nums[:len(expected)],expected);n+=1
  self.assertEqual(n,80)
 def test_existing_early_cohorts_have_no_duplicate_observations(self):
  audit=json.loads((p.BASE/'overlap-check.json').read_text());self.assertEqual(audit['sameNameAndPayCandidates'],[]);self.assertEqual(len(audit['nameCandidates']),4)
 def test_deferred_and_contract_pay_distinct(self):
  audit=json.loads((p.BASE/'1999-00.audit.json').read_text());r=next(x for x in audit['deputies'] if x['name']=='Underleider, C');self.assertEqual(r['amounts'],[117648,14400,27832]);self.assertEqual(p.normalize([r],'deputies','1999-00')[0][3],132048)
  rows=json.loads(gzip.decompress((p.BASE/'2002-03-deputies.json.gzip').read_bytes()));self.assertIn('contracted services',next(r[2] for r in rows if r[1]=='CAMPBELL, D S'))
if __name__=='__main__':unittest.main()
