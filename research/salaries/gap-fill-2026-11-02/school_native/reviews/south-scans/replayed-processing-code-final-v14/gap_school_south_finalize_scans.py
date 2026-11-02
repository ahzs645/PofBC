#!/usr/bin/env python3
"""Deterministic scan source choices; manual receipts and raw candidates stay immutable."""
import gzip,json,hashlib,re
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA
from gap_school_south_scan import FIELDS,comparison
from gap_school_south_dash import is_source_dash

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def ref(p):return {'path':str(p),'sha256':sha(p.read_bytes())}
def run(n):
 old=load(AREA/f'sd{n}-scan-candidate-v6.json.gzip');fresh=load(AREA/f'sd{n}-scan-parsed-v9.json.gzip');assert len(fresh['tesseractRows'])==len(fresh['paddleRows']);cal=json.loads((AREA/'expense-dash-primary-calibration.json').read_text())['calibrations'].get(str(n));glyphs=load(AREA/f'sd{n}-source-expense-glyphs.json.gzip');gs={x['sequence']:x for x in glyphs['features']};paths=sorted(AREA.glob(f'sd{n}-primary-flag-source-readings*.json'));manual={};proofs=[]
 for p in paths:
  d=json.loads(p.read_text());proofs.append(ref(p))
  for r in d['readings']:assert r['sequence'] not in manual;manual[r['sequence']]=r
 oldcoords={(r['pdfPage'],r['sourceY300dpi']):i for i,r in enumerate(old['tesseractRows'],1)}
 extra_path=AREA/f'sd{n}-primary-confidence-and-recovered-source-readings.json';extra={r['sequence']:r for r in json.loads(extra_path.read_text())['readings']} if extra_path.exists() else {}
 if extra_path.exists():proofs.append(ref(extra_path))
 adaptive={}
 for filename in ['adaptive-all13-low-expense-primary-readings.json','adaptive-four-name-space-primary-readings.json']:
  ap=AREA/filename
  if ap.exists():
   proofs.append(ref(ap))
   for ar in json.loads(ap.read_text())['readings']:
    if ar['district']==n:adaptive[ar['sequence']]=ar
 rows=[];flags=[];decisions=[]
 for seq,(one,two) in enumerate(zip(fresh['tesseractRows'],fresh['paddleRows']),1):
  legacy=oldcoords.get((one['pdfPage'],one['sourceY300dpi']))
  r=dict(one);r['legacySequenceV6']=legacy;evidence=[];g=gs.get(legacy)
  if g and cal and all(isinstance(x['expenses'],str) and x['expenses'].startswith('UNRESOLVED:') for x in [one,two]) and is_source_dash(g,cal):r['expenses']=None;evidence.append('complete-source-expense-cell-calibrated-dash')
  before={f:r[f] for f in FIELDS}
  if legacy in manual:
   r.update({f:manual[legacy][f] for f in FIELDS});evidence.append('primary-personal-original-image-reading')
  if seq in extra:
   r.update(extra[seq]['fields']);evidence.append('primary-source-image-confidence-or-recovered-audit')
  if seq in adaptive:
   r.update(adaptive[seq]['fields']);evidence.append('additive-primary-and-peer-adaptive-source-image-audit')
  unresolved=[]
  for f in FIELDS:
   if legacy in manual or seq in extra or seq in adaptive:continue
   if f=='expenses' and 'complete-source-expense-cell-calibrated-dash' in evidence:continue
   if comparison(one[f],f,n)!=comparison(two[f],f,n) or any(isinstance(x[f],str) and x[f].startswith('UNRESOLVED:') for x in [one,two]):unresolved.append(f)
  if n in [35,38,69]:r['name']=r['name'].upper();r['position']=r['position'].upper() if r['position'] else None
  if n==79:
   m=re.match(r'^(\*{1,2})\s*',r['name'])
   if m:r['sourceNameFootnote']=m.group(1);r['sourceNameLiteral']=r['name'];r['name']=r['name'][m.end():]
  rawex=[one.get('sourceExpenseLiteral',''),two.get('sourceExpenseLiteral','')];foot=set()
  if n==35 and any('*' in s for s in rawex):foot.add('*')
  if n==38:
   for s in rawex:foot.update(re.findall(r'\(([1-8])\)',s))
  r['sourceExpenseFootnotes']=sorted(foot)
  if g and cal and is_source_dash(g,cal) and r['expenses'] is not None:unresolved.append('numeric-expense-contradicts-actual-source-dash-ink')
  if not r['name'] or re.search(r'[\d!$|{}:;_<>“”*]',r['name']):unresolved.append('name-syntax-guard')
  if r['position'] is None and n!=78 and not(n==70 and r['category']=='school-trustees'):unresolved.append('unpublished-or-missed-position-needs-source-check')
  if r['position'] and re.search(r'[!$|{}<>_]',r['position']):unresolved.append('position-syntax-guard')
  for f in ['remuneration','expenses']:
   if r[f] is not None:
    try:Decimal(r[f])
    except Exception:unresolved.append(f+'-invalid-number')
  ta=[float(w['conf'])/100 for w in one['tesseractWords'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']]
  ra=[w['confidence'] for w in two['paddleBoxes'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']]
  r['readerConfidenceMinimaNotAccuracyProbabilities']=[min(ta,default=0),min(ra,default=0)]
  if (min(ta,default=0)<.3 or min(ra,default=0)<.7) and not(legacy in manual or seq in extra or seq in adaptive):unresolved.append('low-model-score-requires-pinned-personal-image-reading')
  if unresolved:flags.append({'sequence':seq,'reasons':sorted(set(unresolved)),'chosen':{f:r[f] for f in FIELDS},'freshReaders':[{f:x[f] for f in FIELDS} for x in [one,two]]})
  if not evidence:evidence=['guarded-independent-reader-agreement']
  r['acceptanceEvidence']=evidence;decisions.append({'sequence':seq,'evidence':evidence,'beforePrimaryImage':before,'chosenFields':{f:r[f] for f in FIELDS}});rows.append(r)
 controls={}
 for cat in ['employee-remuneration','school-trustees']:
  xs=[r for r in rows if r['category']==cat];controls[cat]={'rowCount':len(xs),'remuneration':str(sum((Decimal(r['remuneration']) for r in xs if r['remuneration'] and not str(r['remuneration']).startswith('UNRESOLVED:')),Decimal(0))),'expenses':str(sum((Decimal(r['expenses']) for r in xs if r['expenses'] is not None and not str(r['expenses']).startswith('UNRESOLVED:')),Decimal(0))),'nullExpenses':sum(r['expenses'] is None for r in xs)}
 result={'district':n,'rows':rows,'remainingFlags':flags,'controls':controls,'rawReaderReplay':ref(AREA/f'sd{n}-scan-parsed-v9.json.gzip'),'initialCandidate':ref(AREA/f'sd{n}-scan-candidate-v6.json.gzip'),'manualSourceReadings':proofs,'glyphEvidence':ref(AREA/f'sd{n}-source-expense-glyphs.json.gzip'),'decisionLedger':decisions,'status':'candidate-pending-independent-peer-benchmarks-and-controls','noOutreach':True}
 out=AREA/f'sd{n}-scan-reviewed-candidate-v14.json.gzip';out.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps({'district':n,'controls':controls,'remainingFlags':len(flags),'firstFlags':flags[:15]},ensure_ascii=False),flush=True)
if __name__=='__main__':
 for n in [35,38,69,70,78,79]:run(n)
