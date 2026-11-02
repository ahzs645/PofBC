#!/usr/bin/env python3
"""Source-only integer name crops for the expanded word-boundary audit."""
import argparse,gzip,json,math
from pathlib import Path
from gap_school_north_parse import ROOT,AREA,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--full-uppercase',action='store_true');args=ap.parse_args()
 import fitz
 from PIL import Image,ImageDraw
 if args.full_uppercase:
  targets=[]
  for n in [28,54,81]:
   rows=json.loads(gzip.decompress((AREA/f'sd{n:02}-raw-reader-rows.json.gzip').read_bytes()))['readers']['tesseract']
   targets.extend({'number':n,'sequence':i,'physicalPage':r['pdfPage'],'y':r['sourceYPoints']} for i,r in enumerate(rows,1))
 else:targets=json.loads((AREA/'name-spacing-audit-targets.json').read_text())['rows']
 prefix='uppercase-names' if args.full_uppercase else 'name-spacing'
 out=AREA/(prefix+'-images');out.mkdir(exist_ok=True);packets=[];documents={};cache={}
 specs={s['number']:s for s in json.loads((AREA/'ocr-plan.json').read_text())}
 for batch,start in enumerate(range(0,len(targets),24),1):
  selected=targets[start:start+24];images=[]
  for t in selected:
   n,page=t['number'],t['physicalPage'];key=(n,page)
   if n not in documents:documents[n]=fitz.open(specs[n]['path'])
   if key not in cache:
    pix=documents[n][page-1].get_pixmap(dpi=300,alpha=False);cache={key:Image.frombytes('RGB',[pix.width,pix.height],pix.samples)}
   right=310 if n==28 else 220 if n in [54,81] else 240
   box=[0,math.floor((t['y']-6.5)*300/72),math.ceil(right*300/72),math.ceil((t['y']+6.5)*300/72)]
   crop=cache[key].crop(box);images.append((t,box,crop))
  sheet=Image.new('RGB',(max(im.width for _,_,im in images),sum(im.height+23 for _,_,im in images)),'white');draw=ImageDraw.Draw(sheet);y=0;entries=[]
  for t,box,im in images:
   draw.text((4,y+3),f"SD{t['number']:02} physical{t['physicalPage']} sequence{t['sequence']} name-only original300dpi pixels; transcript withheld",fill='black');sheet.paste(im,(0,y+21));entries.append({k:v for k,v in t.items() if k not in ['a','b','previouslyViewed']}|{'originalPixelCrop':box,'sheetY':y+21,'originalPixelSha256':sha(im.tobytes()),'sourceSha256':specs[t['number']]['sha256']});y+=im.height+23
  path=out/f'{prefix}-{batch:02}.png';sheet.save(path);packets.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'reviewedFields':['name'],'rows':entries})
 (AREA/(prefix+'-image-index.json')).write_text(json.dumps({'method':'Source-only exact integer name cell crops from original whole300dpi pages; no resampling and no candidate text on image. '+('All406names in three other uppercase school layouts, widened after shared OCR name-spacing errors were found in SD59.' if args.full_uppercase else 'All raw reader word-boundary disagreements after comma-layout normalization are included.'),'packets':packets,'acceptedRows':0},indent=2)+'\n')

if __name__=='__main__':main()
