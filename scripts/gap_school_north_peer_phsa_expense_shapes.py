from pathlib import Path
import json,hashlib,fitz,cv2,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];B=R/'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
def main():
 cen=json.loads((B/'independent-source-payment-census-first.json').read_text());loc=json.loads((B/'own-source-context-locators.json').read_text());idx={s['sourceKey']:s for s in loc['sources']};out=[];d=B/'own-expense-calibration';d.mkdir(exist_ok=True)
 for s in cen['sources']:
  key=s['sourceKey'];doc=fitz.open(idx[key]['sourceCachePath']);rows=[]
  for pg in s['pages']:
   pix=doc[pg['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(4,4),colorspace=fitz.csGRAY,alpha=False);a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
   for n,r in enumerate(pg['paymentBands'],1):
    box=[480,r['y0']-1.75,565,r['y1']+1.75];crop=a[int(box[1]*4):int(box[3]*4),int(box[0]*4):int(box[2]*4)];mask=(crop<150).astype(np.uint8);count,labels,stats,centroids=cv2.connectedComponentsWithStats(mask,8);keep=np.zeros_like(mask)
    for i in range(1,count):
     if stats[i,4]>=4:keep[labels==i]=1
    ys,xs=np.where(keep)
    width=round((xs.max()-xs.min()+1)/4,2) if len(xs) else 0;height=round((ys.max()-ys.min()+1)/4,2) if len(ys) else 0
    cls='dash-shaped' if 0<height<3 and width<7 else 'narrow-tall-single-glyph-candidate' if height>=3 and width<6 else 'numeric-multiple-glyphs-or-noise' if len(xs) else 'no-ink'
    rows.append(dict(physicalPage=pg['physicalPage'],pageRow=n,clipPoints=box,darkInkWidthPoints=width,darkInkHeightPoints=height,inkPixels=int(keep.sum()),shape=cls))
  by={k:len([r for r in rows if r['shape']==k]) for k in sorted({r['shape'] for r in rows})};print(key,by)
  narrow=[r for r in rows if r['shape'] in ['narrow-tall-single-glyph-candidate','no-ink']];dash=sorted([r for r in rows if r['shape']=='dash-shaped'],key=lambda r:hashlib.sha256(f'{key}/{r["physicalPage"]}/{r["pageRow"]}'.encode()).hexdigest())[:10];selected=narrow+dash;records=[];images=[]
  for i,r in enumerate(selected,1):
   box=[70,r['clipPoints'][1]-1.25,565,r['clipPoints'][3]+1.25];pix=doc[r['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(400/72,400/72),clip=fitz.Rect(*box),alpha=False);p=d/f'{key}-cal{i:03d}-p{r["physicalPage"]:03d}-row{r["pageRow"]:02d}.png';pix.save(p);records.append(dict(id=f'{key}-cal{i:03d}',**r,path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()));images.append((f'{key} C{i:03d} p{r["physicalPage"]} row{r["pageRow"]} {r["shape"]}',Image.open(p).convert('RGB')))
  sheets=[]
  for z in range((len(images)+9)//10):
   a=images[z*10:(z+1)*10];w=max(im.width for _,im in a);h=sum(im.height+35 for _,im in a);sheet=Image.new('RGB',(w,h),'white');draw=ImageDraw.Draw(sheet);y=0
   for label,im in a:draw.text((8,y+5),label,fill='black');sheet.paste(im,(0,y+30));y+=im.height+35
   p=d/f'{key}-calibration-sheet{z+1}.png';sheet.save(p);sheets.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  out.append(dict(sourceKey=key,sourceSha256=s['sourceSha256'],allRows=rows,shapeCounts=by,sourceOnlyCalibrationRecords=records,sourceOnlyCalibrationSheets=sheets))
 p=B/'own-all-expense-shape-source-only-audit.json';assert not p.exists();p.write_text(json.dumps(dict(candidateValuesOpened=False,method='Independent original pixel crop of every expense cell from own payment-band census. Source shapes select personal-review targets only; they are not accepted OCR amounts or proof that a number/zero is present. Narrow/tall and no-ink cells all selected plus10 deterministic dash-shaped source cells per original.',sources=out,noOutreach=True),indent=2)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
