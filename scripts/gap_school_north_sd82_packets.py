#!/usr/bin/env python3
"""SD82 deskewed field sheets from original integer source pixels, without resampling."""
import gzip,json,math,statistics
from pathlib import Path
from gap_school_north_parse import ROOT,AREA,sha

def center(ws,fallback):
 ys=[(w['y0']+w['y1'])/2 for w in ws if w['y1']-w['y0']<=14]
 return statistics.median(ys) if ys else fallback

def main():
 import fitz
 from PIL import Image,ImageDraw
 n=82;targets=[t for t in json.loads((AREA/'source-image-targets.json').read_text())['rows'] if t['number']==82];proof=json.loads(gzip.decompress((AREA/'sd82-raw-reader-rows.json.gzip').read_bytes()));rows=proof['readers']['tesseract'];doc=fitz.open('/workspace/gap-school-north-cache/sd82-sofi-2025.pdf');out=AREA/'image-packets-sd82-v2';out.mkdir(exist_ok=True);packets=[];cache={};bounds=[0,230,385,495,612]
 for batch,start in enumerate(range(0,len(targets),24),1):
  selection=targets[start:start+24];crops=[]
  for t in selection:
   row=rows[t['sequence']-1];page=row['pdfPage']
   if page not in cache:
    pix=doc[page-1].get_pixmap(dpi=300,alpha=False);cache={page:Image.frombytes('RGB',[pix.width,pix.height],pix.samples)}
   im=cache[page];fields=[]
   for k in range(4):
    ws=row['sourceNameWords'] if k==0 else [w for w in row['sourceOtherWords'] if bounds[k]<=w['x0']<bounds[k+1]]
    fallback=row['sourceYPoints']+[0,-1.1,-2.1,-2.8][k];y=center(ws,fallback);box=[math.floor(bounds[k]*300/72),math.floor((y-6.5)*300/72),math.ceil(bounds[k+1]*300/72),math.ceil((y+6.5)*300/72)];crop=im.crop(box);fields.append({'bbox':box,'crop':crop,'centerY':y,'pixelSha256':sha(crop.tobytes())})
   height=max(f['crop'].height for f in fields);line=Image.new('RGB',(im.width,height),'white')
   for k,f in enumerate(fields):line.paste(f['crop'],(math.floor(bounds[k]*300/72),0))
   crops.append((t,fields,line))
  sheet=Image.new('RGB',(2550,sum(c.height+25 for _,_,c in crops)),'white');draw=ImageDraw.Draw(sheet);yy=0;entries=[]
  for t,fields,line in crops:
   draw.text((8,yy+3),f"SD82 p{t['physicalPage']} source sequence{t['sequence']} | name / position / remuneration / expense | exactoriginalpixels field values withheld",fill='black');sheet.paste(line,(0,yy+23));entries.append({**t,'fieldCrops':[{k:v for k,v in f.items() if k!='crop'} for f in fields],'sheetY':yy+23});yy+=line.height+25
  path=out/f'sd82-fields-{batch:02}.png';sheet.save(path);packets.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'sourceSha256':'8e37754ca43a21901aa09506a08017f15d24e0fe89f487a7d32082016dcb6e0a','rows':entries});print(path.name,flush=True)
 (AREA/'sd82-source-field-packet-index-v2.json').write_text(json.dumps({'method':'Independent integer source-field crops from whole original300dpi pages; source slope is compensated only bypasting field crops at alignedsheet y. Originalsourcepixelsarenotresampled. Fullsourceandallboxcoordinatesarepreserved. Supersedes firstSD82 sheetswhichclippedsome monetaryglyphs.','valuesWithheld':True,'packets':packets,'acceptedRows':0},indent=2)+'\n')
if __name__=='__main__':main()
