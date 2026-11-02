"""Source-only pixel-row payment census; no OCR or producer candidate inputs."""
from pathlib import Path
import fitz,numpy as np,hashlib,json
from PIL import Image,ImageDraw
R=Path('/workspace/PofBC');B=Path(__file__).resolve().parent
SPECS={'phsa-2013-14':{'x':[400,475],'start':198,'lastControl':580},'phsa-2014-15':{'x':[385,455],'start':191,'lastControl':540}}
def sha(b):return hashlib.sha256(b).hexdigest()
def groups(profile,cut):
 ys=np.flatnonzero(profile>=cut);out=[]
 for y in ys:
  if out and y-out[-1][-1]<=3:out[-1].append(int(y))
  else:out.append([int(y)])
 return out
def main():
 result=[];targets=[];sheets=[]
 for key,spec in SPECS.items():
  pdf=Path('/workspace/gap-phsa-history-cache')/(key+'.pdf');d=fitz.open(pdf);source=sha(pdf.read_bytes());rows=[];pages=[];unstable=[]
  for pn,p in enumerate(d,1):
   pix=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),colorspace=fitz.csGRAY,alpha=False);a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width);rec={'physicalPage':pn,'rasterDpi':150,'grayPixelSha256':sha(pix.samples),'width':pix.width,'height':pix.height}
   if pn<3:rec['classification']='Library cover' if pn==1 else 'source period/definition/count narrative';pages.append(rec);continue
   calibrations=[]
   for threshold,cut in [(160,3),(120,2),(180,4)]:
    prof=(a[:,round(spec['x'][0]*150/72):round(spec['x'][1]*150/72)]<threshold).sum(axis=1);rs=[];other=[]
    for g in groups(prof,cut):
     y0=g[0]*72/150;y1=g[-1]*72/150
     if y0<=spec['start']:cl='source heading/intro/column label'
     elif y0>=740:cl='statutory footer'
     elif pn==len(d) and y0>=spec['lastControl']:cl='personally read final printed total and its table rules'
     elif y1-y0<3:cl='short scan mark, inspect separately'
     else:cl='named remuneration pixel row';rs.append({'y0':y0,'y1':y1,'darkPixelCount':int(prof[g].sum())})
     other.append({'y0':y0,'y1':y1,'classification':cl})
    calibrations.append({'grayThreshold':threshold,'profileMinimumInkPixels':cut,'namedPixelRows':rs,'allPayColumnRuns':other})
   if len(set(len(x['namedPixelRows']) for x in calibrations))!=1:unstable.append({'physicalPage':pn,'counts':[len(x['namedPixelRows']) for x in calibrations]})
   rs=calibrations[0]['namedPixelRows'];rec['namedPayPixelCount']=len(rs);rec['calibrations']=calibrations;pages.append(rec)
   for row in rs:rows.append({'sourceKey':key,'sequence':len(rows)+1,'physicalPage':pn,**row})
  assert not unstable,unstable
  for seq in sorted(set(1+(len(rows)-1)*j//9 for j in range(10))):
   row=rows[seq-1];p=d[row['physicalPage']-1];pix=p.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
   box=[int(40*300/72),int((row['y0']-4)*300/72),int(570*300/72),int((row['y1']+4)*300/72)];crop=im.crop(box);cp=B/(key+f'-independent-holdout-{seq:04d}.png');crop.save(cp);targets.append({**row,'sourceSha256':source,'dpi':300,'integerCropBox':box,'path':str(cp.relative_to(R)),'sha256':sha(cp.read_bytes()),'reason':'deterministic complete-source pixel-row order; selected before any producer OCR/candidate'})
  result.append({'sourceKey':key,'sourceSha256':source,'allPhysicalPages':len(d),'completePixelNamedRemunerationCount':len(rows),'threeThresholdCountsStable':True,'pixelRows':rows,'allPageEvidence':pages,'noOcrValuesUsed':True,'numericAmountsNotDeterminedByPixelCensus':True})
 for key in SPECS:
  items=[t for t in targets if t['sourceKey']==key]
  for j in range(0,len(items),4):
   chunk=items[j:j+4];ims=[Image.open(R/t['path']) for t in chunk];w=max(i.width for i in ims);h=sum(i.height+35 for i in ims);sheet=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(sheet);y=0
   for t,im in zip(chunk,ims):dr.text((4,y+2),f"{key} physical page{t['physicalPage']} independent pixel sequence{t['sequence']}",fill='black');y+=35;sheet.paste(im,(0,y));y+=im.height
   sp=B/(key+f'-independent-holdout-sheet-{j//4+1}.png');sheet.save(sp);sheets.append({'sourceKey':key,'sequences':[t['sequence'] for t in chunk],'path':str(sp.relative_to(R)),'sha256':sha(sp.read_bytes())})
 out={'phase':'source-only before producer OCR/candidate values','sources':result,'holdoutTargets':targets,'holdoutSheets':sheets,'scope':'Complete original pay-column raster row census, three source-calibrated threshold variants. Does not read or reconstruct monetary values; final printed control zones excluded from named rows from personally viewed originals.','noOutreach':True}
 op=B/'latest-two-scan-independent-pixel-census.json';op.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'path':str(op),'sha256':sha(op.read_bytes()),'sources':[{k:s[k] for k in ['sourceKey','completePixelNamedRemunerationCount']} for s in result],'holdouts':len(targets)},indent=2))
if __name__=='__main__':main()
