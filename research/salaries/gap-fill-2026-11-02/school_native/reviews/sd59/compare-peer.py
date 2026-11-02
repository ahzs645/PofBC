from pathlib import Path
from decimal import Decimal
import json,gzip,hashlib,fitz
A=Path(__file__).parent;ROOT=Path('/workspace/PofBC');C=ROOT/'research/salaries/gap-fill-2026-11-02/school_north/sd59-image-reviewed-candidate.json.gzip';D=ROOT/'research/salaries/gap-fill-school-north/sd59-2024-25-employees.json.gzip';first=A/'first-personal-employee-transcript.txt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(first)=='41343c32637910db019e4108961598eab8ff59fc46c7d8fc44054ecffb72366f'
personal=[x.split('|') for x in first.read_text().splitlines() if x and not x.startswith('#')];j=json.loads(gzip.decompress(C.read_bytes()));candidate=[r for r in j['finalReaders']['tesseract'] if r['category']=='employees'];print('categories',[r['category'] for r in j['finalReaders']['tesseract'][:10]])
if len(candidate)!=248:candidate=j['finalReaders']['tesseract'][7:]
normalized=json.loads(gzip.decompress(D.read_bytes()));assert len(personal)==len(candidate)==len(normalized)==248
fields=['pdfPage','name','position','remuneration','expenses'];diffs=[]
for i,(p,c,n) in enumerate(zip(personal,candidate,normalized),1):
 vals=[int(p[0]),p[1],p[2],Decimal(p[3]),Decimal(p[4])];cv=[c['pdfPage'],c['name'],c['position'],Decimal(c['remuneration']),Decimal(c['expenses'])];nv=[n[5],n[1],n[2],Decimal(str(n[3])),Decimal(str(n[4]))]
 assert cv==nv,(i,cv,nv)
 for field,v,w in zip(fields,vals,cv):
  if v!=w:diffs.append({'employeeSequence':i,'fullSourceSequence':i+7,'physicalPage':int(p[0]),'field':field,'peerFirst':str(v),'candidate':str(w),'sourceYPoints':c['sourceYPoints']})
(A/'first-candidate-comparison.json').write_text(json.dumps({'candidateFile':str(C.relative_to(ROOT)),'candidateSha256Observed':sha(C),'normalizedDataFile':str(D.relative_to(ROOT)),'normalizedDataSha256':sha(D),'allCandidateNormalizedDataExactlyMatch':True,'rowsCompared':248,'differences':diffs},indent=2)+'\n');print(json.dumps(diffs,indent=2))
d=fitz.open('/workspace/gap-school-north-cache/sd59-district-original.pdf')
for x in diffs:
 p=d[x['physicalPage']-1];y=x['sourceYPoints'];p.get_pixmap(dpi=300,alpha=False,clip=fitz.Rect(40,y-12,555,y+15)).save(A/f"fresh-difference-seq{x['employeeSequence']}.png")
