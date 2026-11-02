#!/usr/bin/env python3
"""Low-resolution discovery OCR only; never treated as accepted payment rows."""
import os
os.environ['OMP_THREAD_LIMIT']='1';os.environ['OMP_NUM_THREADS']='1'
import concurrent.futures,gzip,hashlib,json,re,subprocess
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';CACHE=Path('/workspace/gap-municipal-cache')
def process(task):
 s,n=task;key=s['employerSlug']+'-'+s['sha256'][:12];out=AREA/'discovery'/f'{key}-p{n:02d}.json.gzip'
 if out.exists():return json.loads(gzip.decompress(out.read_bytes()))
 doc=fitz.open(s['cachedOriginal']);p=doc[n-1];image=CACHE/f'{key}-discovery-p{n:02d}.png';p.get_pixmap(dpi=150,alpha=False).save(image)
 text=subprocess.check_output(['tesseract',str(image),'stdout','--psm','6'],stderr=subprocess.DEVNULL,text=True);image.unlink()
 r={'sourceKey':key,'sourceSha256':s['sha256'],'physicalPage':n,'discoveryOnly':True,'dpi':150,'text':text}
 out.parent.mkdir(exist_ok=True);out.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False).encode(),mtime=0));print(json.dumps({'key':key,'page':n,'candidate':bool(re.search(r'remuneration|75[,. ]000|employee.?s? name|councillor',text,re.I))}),flush=True);return r

def run():
 r=json.loads((AREA/'refreshed-originals.json').read_bytes());tasks=[];seen=set()
 for s in r['sources']:
  if s['status']!='original-needs-complete-review' or s['sha256'] in seen:continue
  seen.add(s['sha256']);doc=fitz.open(s['cachedOriginal']);native=[]
  for p in doc:
   txt=p.get_text();native.append({'physicalPage':p.number+1,'text':txt})
   if len(txt)<250:tasks.append((s,p.number+1))
  target=AREA/'native-summary'/f"{s['employerSlug']}-{s['sha256'][:12]}.json";target.parent.mkdir(exist_ok=True);target.write_text(json.dumps({'source':s,'pages':native},ensure_ascii=False,indent=2)+'\n')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(process,tasks))
 (AREA/'discovery-summary.json').write_text(json.dumps({'discoveryOnly':True,'scannedPages':len(out),'candidatePages':[r for r in out if re.search(r'remuneration|75[,. ]000|employee.?s? name|councillor',r['text'],re.I)]},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'done':True,'scannedPages':len(out)}))
if __name__=='__main__':run()
