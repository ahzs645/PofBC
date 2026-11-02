from pathlib import Path
from decimal import Decimal
import json,gzip,hashlib
A=Path(__file__).parent;ROOT=Path('/workspace/PofBC');S=ROOT/'research/salaries/gap-fill-2026-11-02/school_south';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((A/'all-first-source-readings-freeze.json').read_text())
for p in freeze['files']:assert sha(ROOT/p['file'])==p['sha256']
raw=[r.split('|') for fn in ['first-personal-flag-and-holdout-transcript.txt','first-personal-complete-trustee-transcript.txt']for r in (A/fn).read_text().splitlines() if r and not r.startswith('#')]
readings={}
for r in raw:
 key=(int(r[0]),int(r[1]));value={'pdfPage':int(r[2]),'name':r[3],'position':None if r[4]=='<blank>'else r[4],'remuneration':r[5],'expenses':None if r[6]=='-'else r[6]}
 if key in readings:assert readings[key]==value
 readings[key]=value
numeric=json.loads((A/'first-personal-expense-glyph-transcript.json').read_text());results=[]
for version in [10,12]:
 for d in [69,70,78]:
  p=S/f'sd{d}-scan-reviewed-candidate-v{version}.json.gzip';j=json.loads(gzip.decompress(p.read_bytes()));rows=j['rows'];diff=[]
  for (district,seq),own in readings.items():
   if district!=d:continue
   row=rows[seq-1]
   for field,v in own.items():
    expected=Decimal(v)if field in ['remuneration','expenses']and v is not None else (' '.join(v.split()).upper()if isinstance(v,str) else v)
    value=row[field];actual=Decimal(value)if field in ['remuneration','expenses']and value is not None else (' '.join(value.split()).upper()if isinstance(value,str) else value)
    if actual!=expected:diff.append({'sequence':seq,'physicalPage':own['pdfPage'],'field':field,'peerFirst':v,'candidate':value,'sourceY300dpi':row.get('sourceY300dpi')})
  glyphdiff=[]
  for seq,value in numeric.get(f'district{d}',{}).items():
   cand=rows[int(seq)-1]['expenses'];want=None if value=='-'else Decimal(value)
   if (Decimal(cand)if cand is not None else None)!=want:glyphdiff.append({'sequence':seq,'peer':value,'candidate':cand})
  results.append({'district':d,'version':version,'candidateFile':str(p.relative_to(ROOT)),'candidateSha256':sha(p),'candidateRows':len(rows),'personalUniqueRows':sum(1 for k in readings if k[0]==d),'differences':diff,'glyphDifferences':glyphdiff,'controls':j['controls'],'remainingFlags':j['remainingFlags']});print(d,version,len(rows),json.dumps(diff),json.dumps(glyphdiff))
(A/'initial-v10-and-v12-source-comparison.json').write_text(json.dumps({'uniquePersonalRows':len(readings),'comparisons':results,'caseConvention':'Comparison ignores repeated whitespace and printed lettercase only; punctuation, spelling, field boundaries, all money/nulls and pages remain exact.'},ensure_ascii=False,indent=2)+'\n')
