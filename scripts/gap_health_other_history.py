#!/usr/bin/env python3
"""Finite nine employee-original extension plus one Fraser source-context copy.

Reuses frozen65 pure reader routines in isolated processes with ONLY their
in-memory output directory bound to this new area. No frozen files are changed.
"""
from __future__ import annotations
import concurrent.futures,copy,datetime,gzip,hashlib,json,pathlib,re,urllib.request,shutil
ROOT=pathlib.Path('/workspace/PofBC');OLD=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees';AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_other_history';CACHE=pathlib.Path('/workspace/gap-health-other-history-cache')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def assets():
 allassets=json.load(open(OLD/'additional-salary-label-original-locators.json'))+json.load(open(OLD/'northern-2014-original-locator.json'));out=[]
 for a in allassets:
  a=copy.deepcopy(a);issuer=a['item']['issuer'];period=re.match(r'(20\d\d)/(20\d\d)',' '.join(a['item']['serialIssue']));assert period
  a['item'].update(candidateYear=period[1]+'/'+period[2][-2:],employerSlug={'Fraser Health':'fraser-health','Northern Health':'northern-health','Vancouver Island Health':'island-health'}[issuer]);a['scopeRole']='context-comparison-only' if issuer=='Fraser Health' else 'employee-salary-candidate';out.append(a)
 assert len(out)==10 and sum(x['scopeRole']=='employee-salary-candidate' for x in out)==9;return out

def download(a):
 url=a['url'];code=sha(url.encode())[:24];p=CACHE/(code+'.pdf');rp=AREA/'retrievals'/(code+'.json')
 if rp.exists():
  r=json.load(open(rp));assert p.exists() and sha(p.read_bytes())==r['responseSha256']
 else:
  response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Public salary source research; ordinary public download','Accept':'application/pdf'}),timeout=120);raw=response.read()
  r={'url':url,'finalUrl':response.url,'status':response.status,'contentType':response.headers.get('Content-Type'),'retrievedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'responseSha256':sha(raw),'bytes':len(raw),'cachePath':str(p),'hasPdfEof':b'%%EOF' in raw[-4096:],'noOutreach':True};assert response.status==200 and raw.startswith(b'%PDF') and r['hasPdfEof'];p.write_bytes(raw);dump(rp,r)
 a=copy.deepcopy(a);a.update(retrieval=r,sourceSha256=r['responseSha256']);return a

def reader_worker(spec):
 # Each entire fitz operation is sequential within one isolated process.
 import fitz
 import gap_health_employees_readers as frozen_reader
 frozen_reader.AREA=AREA
 doc=fitz.open(spec['retrieval']['cachePath']);spec=copy.deepcopy(spec);spec.update(pdfPages=len(doc),repaired=doc.is_repaired);doc.close();e=frozen_reader.one(spec);return spec,e

def visibility_worker(spec):
 import gap_health_employees_visibility as frozen_visibility
 frozen_visibility.AREA=AREA
 return frozen_visibility.one(spec)

def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:found=list(pool.map(download,assets()))
 dump(AREA/'all-ten-originals.json',found);employees=[a for a in found if a['scopeRole']=='employee-salary-candidate']
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:result=list(pool.map(reader_worker,employees))
 specs=[a for a,e in result];evidence=[e for a,e in result];dump(AREA/'recovered-employee-originals-v2.json',specs);dump(AREA/'native-reader-evidence-index-v2.json',evidence)
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:visibility=list(pool.map(visibility_worker,specs))
 dump(AREA/'native-visibility-index-v1.json',visibility);transforms={}
 for s,v in zip(specs,visibility):
  doc=json.loads(gzip.decompress((ROOT/v['path']).read_bytes()));transforms[s['sourceSha256']]=[{k:p[k] for k in ['physicalPage','rotation','rotationMatrix','derotationMatrix','visibleUnrotatedBox']} for p in doc['pages']]
 dump(AREA/'native-page-transforms.json',transforms)
 import gap_health_employees_native as parser
 parser.AREA=AREA
 out=[];native=AREA/'native-candidates';native.mkdir(exist_ok=True)
 for s,e in zip(specs,evidence):
  p=parser.primary(s,e);q=parser.secondary(s,e);p.update(key=e['key'],sourceSha256=s['sourceSha256']);q.update(key=e['key'],sourceSha256=s['sourceSha256']);pr=gzip.compress(json.dumps(p,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);qr=gzip.compress(json.dumps(q,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);pp=native/(e['key']+'-poppler-primary.json.gzip');qp=native/(e['key']+'-mupdf-secondary.json.gzip');pp.write_bytes(pr);qp.write_bytes(qr)
  from collections import Counter
  cp=Counter(tuple(x['row']) for x in p['rows']);cq=Counter(tuple(x['row']) for x in q['rows']);item={'key':e['key'],'sourceSha256':s['sourceSha256'],'file':str(pp.relative_to(ROOT)),'sha256':sha(pr),'secondaryFile':str(qp.relative_to(ROOT)),'secondarySha256':sha(qr),'rows':len(p['rows']),'secondaryRows':len(q['rows']),'pages':len(p['employeePages']),'firstPage':min(p['employeePages']) if p['employeePages'] else None,'lastPage':max(p['employeePages']) if p['employeePages'] else None,'flags':len(p['flags']),'secondaryFlags':len(q['flags']),'rowsExactlyEqual':[r['row'] for r in p['rows']]==[r['row'] for r in q['rows']],'onlyPrimary':list((cp-cq).elements()),'onlySecondary':list((cq-cp).elements()),'controlRows':p['controls']};out.append(item);print(json.dumps({k:v for k,v in item.items() if k not in ['onlyPrimary','onlySecondary','controlRows']}),flush=True)
 dump(AREA/'native-primary-candidate-index.json',out);dump(AREA/'progress.json',{'noOutreach':True,'employeeOriginals':9,'contextOriginals':1,'primaryCandidateRows':sum(r['rows'] for r in out),'sourceAcceptance':False,'pending':['complete actual source context/controls','full physical page and monetary census','native painting/clip audits and independent original-image exceptions','Fraser contract-detail exact overlap comparison; no duplicate append or inferred title join']})
if __name__=='__main__':main()
