from pathlib import Path
import fitz,gzip,hashlib,json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=Path('/workspace/PofBC')
def sha(b):return hashlib.sha256(b).hexdigest()
packet=[];alltargets=[]
for key in ['phsa-2006-07','phsa-2007-08','phsa-2008-09']:
 rows=json.loads(gzip.decompress((B/(key+'-mupdf-independent-rows.json.gzip')).read_bytes()))['rows'];n=len(rows)
 seqs=set(1+(n-1)*j//9 for j in range(10));special={'phsa-2006-07':[97],'phsa-2007-08':[441],'phsa-2008-09':[289]}[key]
 targets=[];pdf=Path('/workspace/gap-phsa-history-cache')/(key+'.pdf');d=fitz.open(pdf)
 for seq in sorted(seqs|set(special)):
  row=rows[seq-1];pn=row['pdfPage'];p=d[pn-1];pix=p.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  box=[int(75*300/72),max(0,int((row['box'][1]-9)*300/72)),min(im.width,int(580*300/72)),min(im.height,int((row['box'][3]+9)*300/72))]
  crop=im.crop(box);cp=B/(key+f'-source-seq{seq:04d}.png');crop.save(cp)
  rec={'sourceKey':key,'sourceSha256':sha(pdf.read_bytes()),'sequence':seq,'physicalPage':pn,'reason':'deterministic original-order holdout' if seq in seqs else 'literal native-reader source flag','integerCropBox':box,'dpi':300,'path':str(cp.relative_to(R)),'sha256':sha(cp.read_bytes())}
  targets.append(rec)
 for j in range(0,len(targets),4):
  chunk=targets[j:j+4];w=max(Image.open(R/x['path']).width for x in chunk);h=sum(Image.open(R/x['path']).height+38 for x in chunk)
  sheet=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(sheet);y=0
  for x in chunk:
   dr.text((4,y+2),f"{key} physical p{x['physicalPage']} sequence{x['sequence']} ({x['reason']})",fill='black');y+=38;im=Image.open(R/x['path']);sheet.paste(im,(0,y));y+=im.height
  sp=B/(key+f'-source-review-sheet-{j//4+1}.png');sheet.save(sp);packet.append({'sourceKey':key,'sequences':[x['sequence'] for x in chunk],'path':str(sp.relative_to(R)),'sha256':sha(sp.read_bytes())})
 alltargets+=targets
(B/'native-source-image-peer-packet.json').write_text(json.dumps({'phase':'source-only before producer candidate','targets':alltargets,'sheets':packet,'sourceRowsManuallyTargeted':len(alltargets),'contextSeparate':True,'candidateValuesWithheld':True,'noOutreach':True},indent=2)+'\n')
print('targets',len(alltargets),'sheets',len(packet))
