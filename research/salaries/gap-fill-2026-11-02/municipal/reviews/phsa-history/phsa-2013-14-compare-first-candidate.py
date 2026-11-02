from pathlib import Path
from decimal import Decimal
import gzip,json,hashlib,re
R=Path('/workspace/PofBC');B=Path(__file__).resolve().parent;P=R/'research/salaries/gap-fill-2026-11-02/phsa_history';cp=P/'phsa-2013-14-scan-candidate-v4.json.gzip';d=json.loads(gzip.decompress(cp.read_bytes()));parts=sorted(B.glob('phsa-2013-14-first-transcript-part-*.json'));expected={r['sequence']:r for p in parts for r in json.loads(p.read_text())['rows']};expected[64]={**expected[64],'name':'Anderson, Genevieve Savannagh'}
for r in json.loads((B/'latest-two-scans-first-independent-holdout-transcript.json').read_text())['rows']:
 if r['sourceKey']=='phsa-2013-14':expected.setdefault(r['sequence'],r)
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s or '').strip()) if isinstance(s,str) else s
res=[]
for seq,a in sorted(expected.items()):
 row=d['rows'][seq-1];diffs={}
 for reader in ['tesseract','rapid','selected']:
  b=row[reader];fields={'name':b.get('name'),'position':None,'remuneration':b['pay']['value'],'expenses':b['expense']['value'],'pdfPage':row['physicalPage']} if reader!='selected' else b
  fs={f:{'sourceImageReading':a[f],'readerValue':fields[f]} for f in ['name','position','remuneration','expenses','pdfPage'] if norm(a[f])!=norm(fields[f])}
  if fs:diffs[reader]=fs
 if diffs:res.append({'sequence':seq,'pdfPage':row['physicalPage'],'differences':diffs,'sourceImagePath':a.get('sourceImagePath',a.get('sourceCropPath'))})
out={'phase':'first candidate comparison after all422first source readings frozen','sourceKey':'phsa-2013-14','candidatePin':{'path':str(cp.relative_to(R)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest()},'firstTranscriptIndexSha256':hashlib.sha256((B/'phsa-2013-14-first-transcript-index.json').read_bytes()).hexdigest(),'priorSourceOnlyRereadApplied':[64],'uniqueManualRowsCompared':len(expected),'perReaderDifferentRowCounts':{k:sum(k in r['differences'] for r in res) for k in ['tesseract','rapid','selected']},'differences':res,'noFieldAdjustedFromTotals':True,'noOutreach':True}
p=B/'phsa-2013-14-first-candidate-comparison.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print({k:v for k,v in out.items() if k not in ['differences','candidatePin']});print('selected differences',[{'sequence':r['sequence'],'fields':r['differences']['selected']} for r in res if 'selected'in r['differences']]);print('sha',hashlib.sha256(p.read_bytes()).hexdigest())
