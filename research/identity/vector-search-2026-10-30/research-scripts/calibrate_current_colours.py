from pathlib import Path
import json,fitz,numpy as np,xml.etree.ElementTree as ET,hashlib,collections
B=Path(__file__).resolve().parent
records=json.loads((B/'current-crown-vectors/extraction-metadata.json').read_text())
SCALE=6
for r in records:
 path=Path(r['localFile']);raw=path.read_bytes();tree=ET.fromstring(raw)
 crop=fitz.Rect(r['crop']);doc=fitz.open(r['sourceFile']);pix=doc[r['sourcePage']-1].get_pixmap(matrix=fitz.Matrix(SCALE,SCALE),clip=crop,alpha=False)
 src=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
 svg=fitz.open(path);vp=svg[0].get_pixmap(matrix=fitz.Matrix(SCALE,SCALE),alpha=True)
 arr=np.frombuffer(vp.samples,dtype=np.uint8).reshape(vp.height,vp.width,4)
 colours=set()
 for node in tree.iter():
  for attr in ['fill','stroke']:
   c=node.get(attr)
   if c and c.startswith('#') and len(c)==7:colours.add(c)
 mapped=[]
 for c in sorted(colours):
  rgb=np.array([int(c[i:i+2],16) for i in (1,3,5)])
  mask=(np.max(np.abs(arr[:,:,:3].astype(int)-rgb),axis=2)<=1)&(arr[:,:,3]==255)
  # Keep only flat interiors, away from antialiasing and neighbouring fills.
  for dy,dx in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,2),(-2,2),(2,-2)]:
   mask &= np.roll(np.roll(np.max(np.abs(arr[:,:,:3].astype(int)-rgb),axis=2)<=1,dy,axis=0),dx,axis=1)
  ys,xs=np.where(mask)
  sx=np.floor(crop.x0*SCALE+xs+.5-pix.x).astype(int);sy=np.floor(crop.y0*SCALE+ys+.5-pix.y).astype(int)
  valid=(sx>=0)&(sy>=0)&(sx<pix.width)&(sy<pix.height);sx=sx[valid];sy=sy[valid]
  if len(sx)<30:continue
  samples=src[sy,sx]
  vals,counts=np.unique(samples,axis=0,return_counts=True);imax=np.argmax(counts);target=vals[imax];modecount=int(counts[imax]);confidence=modecount/len(samples)
  targethex='#'+''.join(f'{v:02x}' for v in target)
  delta=int(np.max(np.abs(rgb-target)))
  if confidence<.70:print('UNSTABLE',r['id'],c,targethex,confidence,len(samples));continue
  # Ignore inconsequential rounding differences; correct substantial ICC conversion.
  if delta>=3:
   for node in tree.iter():
    for attr in ['fill','stroke']:
     if node.get(attr)==c:node.set(attr,targethex)
   mapped.append(dict(originalExportedRGB=c,sourceRenderedSRGB=targethex,interiorSamples=len(samples),modeCount=modecount,modeShare=round(confidence,6),maxChannelDifference=delta))
 if mapped:
  (B/'current-crown-sources'/f'{r["id"]}-native-export.svg').write_bytes(raw)
  raw=ET.tostring(tree,encoding='utf-8',xml_declaration=True);path.write_bytes(raw)
  r['nativeExportSha256']=r['sha256'];r['sha256']=hashlib.sha256(raw).hexdigest()
  r['colourConversion']={'method':'Map flat fully opaque source colours to the modal sRGB of matching interior pixels rendered from the official PDF at 6x with PyMuPDF colour management; geometry unchanged. Anti-aliased boundary pixels excluded. No inferred brand palette.','sourceSha256':r['sourceSha256'],'mappings':mapped}
  r['colourNote']='SVG colours calibrated to opaque colour-managed source PDF sRGB; all mappings and sample confidence recorded. No palette inferred or replaced from external references.'
  r['extraction'] += ' Source PDF ICC/CMYK colours explicitly converted to their rendered sRGB where naive SVG conversion differed; mapping recorded separately.'
 print(r['id'],mapped)
(B/'current-crown-vectors/extraction-metadata.json').write_text(json.dumps(records,indent=2))
