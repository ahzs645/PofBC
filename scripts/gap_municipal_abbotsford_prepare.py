#!/usr/bin/env python3
"""Bound only eleven previously held known-column rows; preserve the accepted449."""
import hashlib,json,math
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';CACHE=Path('/workspace/gap-municipal-cache')
if __name__=='__main__':
 path=ROOT/'research/salaries/municipal-wave-lower-mainland/sources.json';raw=path.read_bytes();old=next(s for s in json.loads(raw)['sources'] if s['id']=='wave-lower-mainland-city-of-abbotsford-2023-employee-remuneration');held=old['validation']['heldRows'];assert len(held)==11
 r=json.loads((AREA/'refreshed-originals.json').read_bytes());src=next(s for s in r['sources'] if s['leadId']=='lead-026');assert src['sha256']==old['sha256'];pdf=Path(src['cachedOriginal']);assert hashlib.sha256(pdf.read_bytes()).hexdigest()==old['sha256'];doc=fitz.open(pdf)
 cropdir=AREA/'abbotsford-known-column-crops';cropdir.mkdir(exist_ok=True);spec=[]
 for i,row in enumerate(held,1):
  pn=row['pdfPage'];page=doc[pn-1];matches=page.search_for(row['name']);assert len(matches)==1,(row['name'],matches)
  rect=matches[0];pix=page.get_pixmap(dpi=300,alpha=False);full=CACHE/f'abbotsford2023-p{pn:02d}-300dpi.png';pix.save(full)
  bounds=[0,max(0,math.floor((rect.y0-4)*300/72)),pix.width,min(pix.height,math.ceil((rect.y1+8)*300/72))];image=Image.open(full);crop=image.crop(bounds);out=cropdir/f'held-row-{i:02d}.png';crop.save(out)
  spec.append({'ordinal':i,'sourceName':row['name'],'physicalPage':pn,'sourceSha256':src['sha256'],'fullPage300DpiSha256':hashlib.sha256(full.read_bytes()).hexdigest(),'fullPageRuntimeImage':str(full),'pixelCropBounds':bounds,'crop':str(out.relative_to(ROOT)),'cropSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'priorHeldRow':row,'candidateValuesWithheldInIndependentPacket':True})
 olddata=ROOT/'research/salaries/municipal-wave-lower-mainland'/old['file'];assert hashlib.sha256(olddata.read_bytes()).hexdigest()==old['dataSha256']
 proof={'sourceId':old['id'],'sourceSha256':src['sha256'],'priorManifest':{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()},'priorAcceptedRows':449,'priorSourceNamedRows':460,'priorData':{'path':str(olddata.relative_to(ROOT)),'sha256':old['dataSha256']},'exactPriorHeldRows':held,'exactPriorHeldRowsSha256':hashlib.sha256(json.dumps(held,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'proposedDefinition':'Known Remuneration & Payouts column only; excludes an unpublished/dash separate Taxable Benefit. Partial compensation, not complete composite compensation. No missing benefit zero, no old row replacement or metadata edit.','candidateOnly':True,'noOutreach':True,'cropSpecs':spec}
 (AREA/'abbotsford-known-column-supplement.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('Prepared11 literal source crops and exact previous449/11held split.')
