#!/usr/bin/env python3
"""Refresh eight original Ministry school reports and bounded OCR discovery."""
import argparse,hashlib,json,urllib.request,subprocess,gzip,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_north';CACHE=Path('/workspace/gap-school-north-cache');CACHE.mkdir(exist_ok=True)
def packed(p,v):p.write_bytes(gzip.compress(json.dumps(v,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def refresh():
 leads=json.loads((AREA/'assigned-leads.json').read_text());result=[]
 for x in leads:
  key=x['sourceUrl'].split('/')[-1];p=CACHE/key;trials=[]
  for trial in range(3):
   try:
    with urllib.request.urlopen(urllib.request.Request(x['sourceUrl'],headers={'User-Agent':'PofBC salary source audit'}),timeout=90) as r:raw=r.read();status=r.status;final=r.url
    assert raw.startswith(b'%PDF'),raw[:100];p.write_bytes(raw);trials.append({'status':status,'url':final,'bytes':len(raw)});break
   except Exception as e:trials.append({'error':str(e)})
  if not p.exists():
   old=Path('/tmp/pofbc-schools')/('ministry-sd'+key.split('-')[0][2:]+'-2025.pdf');assert old.exists(),old;p.write_bytes(old.read_bytes())
  import fitz
  doc=fitz.open(p);item={'leadId':x['id'],'sourceUrl':x['sourceUrl'],'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'pages':len(doc),'refreshTrials':trials,'refreshSucceeded':any(q.get('status')==200 for q in trials)};result.append(item);print(json.dumps(item),flush=True)
 (AREA/'refreshed-originals.json').write_text(json.dumps(result,indent=2)+'\n')
def discover(kind):
 import fitz
 out=[]
 for spec in json.loads((AREA/'refreshed-originals.json').read_text()):
  doc=fitz.open(spec['path']);key=Path(spec['path']).stem
  pages=range(1,min(4,len(doc))+1) if kind=='front' else range(max(1,len(doc)-24),len(doc)+1)
  for num in pages:
   path=AREA/(key+f'-discovery-p{num:03}.json.gzip')
   if path.exists():continue
   page=doc[num-1];png=CACHE/(key+'-scratch.png');pix=page.get_pixmap(dpi=125);pix.save(png)
   text=subprocess.check_output(['tesseract',str(png),'stdout','--psm','3'],stderr=subprocess.DEVNULL).decode()
   item={'sourceSha256':spec['sha256'],'sourceUrl':spec['sourceUrl'],'physicalPage':num,'dpi':125,'reader':'Tesseract5.5 psm3 discovery only','text':text};packed(path,item)
   print(key,num,text[:90].replace('\n',' '),flush=True)
  png.unlink(missing_ok=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');p.add_argument('--discover',choices=['front','tail']);a=p.parse_args()
 if a.refresh:refresh()
 if a.discover:discover(a.discover)
if __name__=='__main__':main()
