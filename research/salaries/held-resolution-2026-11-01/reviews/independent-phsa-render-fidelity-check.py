import fitz,gzip,hashlib,json,time
from pathlib import Path
from PIL import Image,ImageChops,ImageFilter
ROOT=Path('/workspace/PofBC');OUT=Path('/tmp/independent-phsa-render-fidelity');OUT.mkdir(exist_ok=True)
PDF=Path('/tmp/sector-health/phsa-2025.pdf');SOURCE_SHA='809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c';assert hashlib.sha256(PDF.read_bytes()).hexdigest()==SOURCE_SHA
pdf=fitz.open(PDF);assert len(pdf)==284;lut=[255 if v<128 else 0 for v in range(256)];pageproof=[];rowsproof=[];exceptions=[];bandexceptions=[]
def count(mask):return sum(mask.histogram()[1:])
for pn in range(1,285):
 ep=Path(f'/tmp/held-health-ocr/full/pages/p{pn:03d}.json.gzip');eraw=ep.read_bytes();e=json.loads(gzip.decompress(eraw));rows=e['rowEvidence'];assert e['physicalPage']==pn and e['sourceSha256']==SOURCE_SHA
 p=OUT/f'true-p{pn:03d}.png'
 if not p.exists():pdf[pn-1].get_pixmap(dpi=300,alpha=False).save(p)
 nativep=Path(e['imagePath']);actual=Image.open(p).convert('RGB');native=Image.open(nativep).convert('RGB');assert actual.size==native.size==(2550,3300)
 assert hashlib.sha256(nativep.read_bytes()).hexdigest()==e['imageSha256'];a=actual.convert('L').point(lut);b=native.convert('L').point(lut)
 box=(190,685,2210,3070);aa=a.crop(box);bb=b.crop(box);aonly=ImageChops.subtract(aa,bb.filter(ImageFilter.MaxFilter(3)));bonly=ImageChops.subtract(bb,aa.filter(ImageFilter.MaxFilter(3)))
 bandbottom=2600 if pn==284 else 3070;projection=a.crop((190,685,1600,bandbottom)).getprojection()[1];bands=[]
 for y,ink in enumerate(projection,685):
  if not ink:continue
  if not bands or y-bands[-1][1]>8:bands.append([y,y])
  else:bands[-1][1]=y
 deltas=[]
 if len(bands)!=len(rows):bandexceptions.append({'physicalPage':pn,'bitmapNameBands':len(bands),'ocrRows':len(rows),'bands':bands})
 else:
  for band,r in zip(bands,rows):
   center=sum(band)/2;deltas.extend([abs(center-r['tesseract']['y']),abs(center-r['rapidocr']['y'])])
  if max(deltas,default=0)>10:bandexceptions.append({'physicalPage':pn,'kind':'row-center-disagreement','maxDelta':max(deltas)})
 for r in rows:
  y=round(r['tesseract']['y']);fields={}
  for field,(left,right) in {'name':(190,1600),'remuneration':(1600,1930),'expenses':(1930,2210)}.items():
   fullbox=(left,y-25,right,y+25);local=(left-190,y-25-685,right-190,y+25-685)
   fields[field]={'binaryPixelsDifferent':count(ImageChops.difference(a.crop(fullbox),b.crop(fullbox))),'actualInkWithoutNativeWithin1Pixel':count(aonly.crop(local)),'nativeInkWithoutActualWithin1Pixel':count(bonly.crop(local))}
  item={'physicalPage':pn,'sourceRowOnPage':r['sourceRowOnPage'],'fields':fields};rowsproof.append(item)
  if any(v['actualInkWithoutNativeWithin1Pixel'] or v['nativeInkWithoutActualWithin1Pixel'] for v in fields.values()):exceptions.append(item)
 pageproof.append({'physicalPage':pn,'actualPdfRenderSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeImageSha256':e['imageSha256'],'rawPageEvidenceSha256':hashlib.sha256(eraw).hexdigest(),'nativeRows':len(rows),'actualBitmapNameBands':len(bands),'maxNameBandCenterDelta':max(deltas,default=None),'bodyActualOnlyInkPixelsAt1Pixel':count(aonly),'bodyNativeOnlyInkPixelsAt1Pixel':count(bonly)})
 print(json.dumps({'page':pn,'rows':len(rows),'bitmapBands':len(bands),'exceptionRowsSoFar':len(exceptions)}),flush=True)
summary={'sourceSha256':SOURCE_SHA,'physicalPdfPages':284,'processedPages':len(pageproof),'comparedNamedRows':len(rowsproof),'method':'Every actual PDF page rendered at300dpi using PyMuPDF page.get_pixmap(dpi=300,alpha=False); compare against original native tile image at2550x3300. Binary ink means grayscale<128. Every name/pay/expense ink pixel must have an opposite-view ink counterpart within1pixel using a3x3maxfilter. Exact binary differences are also counted, without pretending antialiasing images are identical.','nameBandMethod':'Independently project actual source ink in fixed name-column ROI x190:1600,y685:3070; merge vertical ink gaps at most8pixels. Final page uses y685:2600, excluding the separately identified ruled Total row. Compare band count and each band center to both independent OCR geometries, tolerance10pixels (row spacing about48pixels). No assumption that earlier pages have49rows.','rowsWithUnmatchedInk':exceptions,'nameBandExceptions':bandexceptions,'pageProof':pageproof,'rows':rowsproof,'acceptanceClaim':False}
(OUT/'all284-source-fidelity-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['processedPages','comparedNamedRows','rowsWithUnmatchedInk','nameBandExceptions']}),flush=True)
