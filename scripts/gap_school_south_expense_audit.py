#!/usr/bin/env python3
"""Adaptive original-source audit for all low numeric expense cells in SD35/38."""
import gzip,json,hashlib,math
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE

def sha(b):return hashlib.sha256(b).hexdigest()
def run():
 import fitz
 from PIL import Image,ImageDraw
 out=AREA/'adaptive-review-images';out.mkdir(exist_ok=True);targets=[];ims=[]
 for n in [35,38]:
  d=json.loads(gzip.decompress((AREA/f'sd{n}-scan-reviewed-candidate-v12.json.gzip').read_bytes()));doc=fitz.open(CACHE/f'sd{n}-sofi-2025.pdf');pages={}
  for seq,r in enumerate(d['rows'],1):
   if r['expenses'] is None or not 0<=float(r['expenses'])<10:continue
   p=r['pdfPage'];cy=r['sourceY300dpi']
   if p not in pages:
    pix=doc[p-1].get_pixmap(dpi=300);pages[p]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
   box=[20,max(0,math.floor(cy-25)),min(2460,pages[p].width),math.ceil(cy+25)];im=pages[p].crop(box);path=out/f'sd{n}-single-digit-expense-seq{seq}-source300.png';im.save(path);targets.append({'district':n,'sequence':seq,'physicalPage':p,'integerBox300Dpi':box,'path':str(path),'sha256':sha(path.read_bytes())});ims.append(im)
 canvas=Image.new('RGB',(2440,len(ims)*80),'white');dr=ImageDraw.Draw(canvas)
 for j,(t,im) in enumerate(zip(targets,ims)):dr.text((10,j*80),f'SD{t["district"]} seq{t["sequence"]} p{t["physicalPage"]} SOURCE',fill='black');canvas.paste(im,(0,j*80+22))
 canvas.save(out/'all13-single-digit-expense-source-sheet.png');(AREA/'adaptive-all13-low-expense-source-only-packet.json').write_text(json.dumps({'targets':targets,'reason':'Peer caught two primary numeric7 selections where original source shows a dash. Both priorOCR alternatives and earlier mistaken primary receipts retained. Broadened to every selected numeric expense<10 in SD35/38.','noChosenValuesIncluded':True},indent=2)+'\n')
if __name__=='__main__':run()
