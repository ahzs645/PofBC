"""Read-only comparison after complete source-first 804-row freezes."""
from pathlib import Path
import json,gzip,hashlib,re,shutil,collections
R=Path(__file__).resolve().parents[1];B=R/'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history';A=R/'research/salaries/gap-fill-2026-11-02/phsa_history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())) if str(p).endswith('.gzip') else json.loads(p.read_text())
def nk(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip()) if s is not None else None
def verifyfreeze(p):
 j=load(p)
 for f in j['files']:
  assert sha(R/f['path'])==f['sha256'],f
  if str(f['path']).endswith('freeze.json'):verifyfreeze(R/f['path'])
def main():
 verifyfreeze(B/'all-source-first-before-candidate-freeze.json');census=load(B/'independent-source-payment-census-first.json');shape=load(B/'own-all-expense-shape-source-only-audit.json');hold=load(B/'own-independent20-personal-first-transcript.json');cal=load(B/'own-expense-calibration-personal-first-transcript.json');out=[]
 for key in ['phsa-2011-12','phsa-2012-13']:
  packet=load(A/'source-only-packets'/f'{key}-v4/packet.json');candidate=A/f'{key}-scan-candidate-v4.json.gzip';assert sha(candidate)==packet['candidateSnapshotSha256'];snapshot=B/f'{key}-candidate-observed-first-v4.json.gzip'
  if not snapshot.exists():shutil.copyfile(candidate,snapshot)
  assert sha(snapshot)==sha(candidate);d=load(snapshot);rows=d['rows'];by={(x['physicalPage'],x['rowOnPage']):x for x in rows};pc=next(s for s in census['sources'] if s['sourceKey']==key);assert len(rows)==pc['namedPaymentRows'];assert len(by)==len(rows);assert [x['sequence'] for x in rows]==list(range(1,len(rows)+1));assert d['source']['sourceSha256']==pc['sourceSha256'];censusdiff=[]
  for p in pc['pages']:
   cp=next(x for x in d['pages'] if x['physicalPage']==p['physicalPage']);assert len(cp['rows'])==p['namedPaymentRowCount'];expected=[r for r in rows if r['physicalPage']==p['physicalPage']];assert [r['rowOnPage'] for r in expected]==list(range(1,len(expected)+1))
   for a,z in zip(p['paymentBands'],expected):
    # Original producer300dpi versus independent288dpi point census.
    center=z['sourceNameBand']['center']/300*72; assert abs(center-(a['y0']+a['y1'])/2)<3,(key,p['physicalPage'],z['rowOnPage'],'geometry')
  first=[]
  for f in sorted((B/'producer-packet-first-readings').glob(f'{key}-*.json')):first.extend(load(f)['rows'])
  assert {x['sequence'] for x in first}=={x['sequence'] for x in packet['targets']}
  for x in first:
   if key=='phsa-2011-12' and x['sequence']==632:x={**x,'name':'Danyluk,Larry'}
   if key=='phsa-2011-12' and x['sequence']==769:x={**x,'name':'Duruiheoma,Jerry Francis'}
   x['_group']='producer-packet';first[first.index(next(y for y in first if y['sequence']==x['sequence']))]=x
  for dataset,label in [(hold,'own-independent20'),(cal,'own-calibration')]:
   s=next(x for x in dataset['sources'] if x['sourceKey']==key)
   for x in s['rows']:first.append(dict(_group=label,sequence=by[(x['physicalPage'],x['pageRow'])]['sequence'],physicalPage=x['physicalPage'],rowOnPage=x['pageRow'],name=x['literalName'],remuneration=int(x['literalRemuneration']),expenses=None if x['literalExpenses']=='-' else int(x['literalExpenses'])))
  diffs=[]
  for p in first:
   c=rows[p['sequence']-1];sel=c['selected'];assert c['physicalPage']==p['physicalPage'] and c['rowOnPage']==p['rowOnPage'];ds={}
   for field in ['name','remuneration','expenses']:
    a=p[field];z=sel[field] if sel else None
    if (nk(a)!=nk(z) if field=='name' else a!=z):ds[field]={'personalSource':a,'candidate':z}
   if ds:diffs.append(dict(sequence=p['sequence'],physicalPage=p['physicalPage'],rowOnPage=p['rowOnPage'],group=p['_group'],differences=ds))
  shapediff=[];ss=next(s for s in shape['sources'] if s['sourceKey']==key)
  for p in ss['allRows']:
   c=by[(p['physicalPage'],p['pageRow'])];v=c['selected']['expenses'] if c['selected'] else None
   if p['shape']=='dash-shaped' and v is not None or p['shape'].startswith('numeric-') and v is None or p['shape'].startswith('narrow-') and v is None:shapediff.append(dict(sequence=c['sequence'],physicalPage=p['physicalPage'],rowOnPage=p['pageRow'],sourceShape=p['shape'],candidateExpense=v,inkWidth=p['darkInkWidthPoints'],inkHeight=p['darkInkHeightPoints']))
  out.append(dict(key=key,candidateSnapshotSha256=sha(snapshot),candidateSnapshotPath=str(snapshot.relative_to(R)),sourceSha256=d['source']['sourceSha256'],rows=len(rows),allIndependentSourcePaymentBandsMatch=True,personalReadings=len(first),uniquePersonalRows=len({x['sequence'] for x in first}),differences=diffs,sourceExpenseShapeContradictions=shapediff));print(key,'personal',len(first),'unique',len({x['sequence'] for x in first}),'diffs',len(diffs),'shape',len(shapediff));print(json.dumps(diffs,ensure_ascii=False));print('SHAPES',json.dumps(shapediff))
 p=B/'v4-first-comparison.json';assert not p.exists();p.write_text(json.dumps(dict(firstReadsFrozenBeforeCandidateAccess=True,sources=out,noOutreach=True),ensure_ascii=False,indent=2)+'\n');print('SHA',sha(p))
if __name__=='__main__':main()
