from pathlib import Path
import hashlib,json,fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 census=json.loads((B/'independent-source-payment-census-first.json').read_text());loc=json.loads((B/'own-source-context-locators.json').read_text());idx={s['sourceKey']:s for s in loc['sources']};out=[];d=B/'own-holdout-source-images';d.mkdir(exist_ok=True)
 for s in census['sources']:
  key=s['sourceKey'];allrows=[dict(physicalPage=p['physicalPage'],pageRow=i+1,**r) for p in s['pages'] for i,r in enumerate(p['paymentBands'])];rank=sorted(allrows,key=lambda r:hashlib.sha256(f"{s['sourceSha256']}/north-peer-independent20/{r['physicalPage']}/{r['pageRow']}".encode()).hexdigest());selected=sorted(rank[:20],key=lambda r:(r['physicalPage'],r['pageRow']));doc=fitz.open(idx[key]['sourceCachePath']);records=[];images=[]
  for n,r in enumerate(selected,1):
   box=[70,r['y0']-3,565,r['y1']+3];pix=doc[r['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(400/72,400/72),clip=fitz.Rect(*box),alpha=False);p=d/f'{key}-holdout{n:02d}-p{r["physicalPage"]:03d}-row{r["pageRow"]:02d}.png';pix.save(p);records.append(dict(id=f'{key}-holdout{n:02d}',physicalPage=r['physicalPage'],pageRow=r['pageRow'],clipPoints=box,dpi=400,path=str(p.relative_to(ROOT)),sha256=sh(p)));images.append((f'{key} H{n:02d} source p{r["physicalPage"]} row{r["pageRow"]}',Image.open(p).convert('RGB')))
  sheets=[]
  for z in range(2):
   a=images[z*10:(z+1)*10];w=max(im.width for _,im in a);h=sum(im.height+35 for _,im in a);sheet=Image.new('RGB',(w,h),'white');draw=ImageDraw.Draw(sheet);y=0
   for label,im in a:draw.text((8,y+5),label,fill='black');sheet.paste(im,(0,y+30));y+=im.height+35
   p=d/f'{key}-holdout-sheet{z+1}.png';sheet.save(p);sheets.append(dict(path=str(p.relative_to(ROOT)),sha256=sh(p)))
  out.append(dict(sourceKey=key,sourceSha256=s['sourceSha256'],candidateValuesWithheld=True,selection='Lowest20 SHA256(source SHA/north-peer-independent20/physicalPage/pageRow), source pixel census locators only; no producer row values/flags consulted.',records=records,sheets=sheets))
 p=B/'own-independent20-source-only-packet.json';assert not p.exists();p.write_text(json.dumps(dict(candidateValuesOpened=False,sources=out,noOutreach=True),indent=2)+'\n');print(sh(p))
if __name__=='__main__':main()
