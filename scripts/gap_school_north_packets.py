#!/usr/bin/env python3
"""Source-only review sheets: integer crops from original whole-page300dpi renders."""
import hashlib,json,math
from pathlib import Path
from gap_school_north_parse import AREA,ROOT,sha

def main():
 import fitz
 from PIL import Image,ImageDraw,ImageFont
 targets=json.loads((AREA/'source-image-targets.json').read_text())['rows'];specs={x['number']:x for x in json.loads((AREA/'ocr-plan.json').read_text())};out=AREA/'image-packets';out.mkdir(exist_ok=True);index=[]
 for n in specs:
  selected=[x for x in targets if x['number']==n];spec=specs[n];doc=fitz.open(spec['path']);rendered={}
  for batchno,start in enumerate(range(0,len(selected),24),1):
   batch=selected[start:start+24];crops=[];width=0
   for t in batch:
    page=t['physicalPage']
    if page not in rendered:
     pix=doc[page-1].get_pixmap(dpi=300,alpha=False);rendered={page:Image.frombytes('RGB',[pix.width,pix.height],pix.samples)}
    img=rendered[page];half=3.8 if n==54 else 4.8 if n==58 else 5.3;y=t['y'];bbox=[0,math.floor((y-half)*300/72),img.width,math.ceil((y+half)*300/72)];crop=img.crop(bbox);width=max(width,crop.width);crops.append((t,bbox,crop))
   height=sum(c.height+24 for _,_,c in crops)+4;sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet);yy=0;entries=[]
   for t,bbox,c in crops:
    draw.text((8,yy+3),f"SD{n:02}   physical page {t['physicalPage']}   source sequence {t['sequence']}   field values withheld",fill='black');sheet.paste(c,(0,yy+22));entries.append({**t,'originalPixelCrop':bbox,'sheetY':yy+22,'cropPixelSha256':sha(c.tobytes())});yy+=c.height+24
   path=out/f'sd{n:02}-sheet-{batchno:02}.png';sheet.save(path);index.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'sourceSha256':spec['sha256'],'sourceUrl':spec['sourceUrl'],'render':'Full original page300dpi, integer crop pasted at1:1; no source pixels resampled or annotated','rows':entries});print(path.name,len(entries),flush=True)
 (AREA/'source-image-packet-index.json').write_text(json.dumps({'valuesWithheld':True,'packets':index,'acceptedRows':0},indent=2)+'\n')
if __name__=='__main__':main()
