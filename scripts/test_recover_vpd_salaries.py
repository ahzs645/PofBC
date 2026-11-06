import copy,gzip,hashlib,json,unittest
from pathlib import Path
from recover_vpd_salaries import OUT,build,parse_anonymous,remove_named_overlap,total
class RecoveryTest(unittest.TestCase):
 def test_deterministic_offline_rebuild(self):
  build();files=list(OUT.glob('*.json.gzip'))+[OUT/'sources.json',OUT/'validation.json']+list((OUT/'evidence').glob('*.json.gzip'))
  before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};build()
  self.assertEqual(before,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
 def test_overlap_and_totals(self):
  original=parse_anonymous();named=json.loads(gzip.decompress((OUT/'2009-named.json.gzip').read_bytes()));residual,ledger=remove_named_overlap(original,named)
  self.assertEqual((len(original),len(residual),len(named),len(ledger)),(1212,1125,87,87))
  self.assertTrue(all(r[1] is None for r in residual))
  for at in [3,4]:self.assertEqual(total(original,at),total(residual+named,at))
 def test_ambiguous_or_missing_overlap_fails(self):
  original=parse_anonymous();named=json.loads(gzip.decompress((OUT/'2009-named.json.gzip').read_bytes()))
  copy_rows=copy.deepcopy(original);hit=next(r for r in original if r[3:5]==named[0][3:5]);copy_rows.append(hit)
  with self.assertRaises(AssertionError):remove_named_overlap(copy_rows,named)
  named[0][3]+=0.01
  with self.assertRaises(AssertionError):remove_named_overlap(original,named)
 def test_categories_expenses_and_scope(self):
  sources=build()['sources'];self.assertEqual(sum(s['rowCount'] for s in sources),1237)
  self.assertEqual([s['category'] for s in sources],['employee-remuneration','employee-remuneration','executive-only'])
  self.assertTrue(all(not s['completeEmployeeSchedule'] for s in sources))
  anonymous=json.loads(gzip.decompress((OUT/'2009-anonymous-residual.json.gzip').read_bytes()))
  self.assertTrue(any(r[4] is None for r in anonymous))
if __name__=='__main__':unittest.main()
