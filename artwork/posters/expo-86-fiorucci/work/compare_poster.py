"""Geometric QA only. Image masks measure authored vector contours;
they are never converted to vector paths or used to generate artwork.
"""
from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from lxml import etree as ET

BASE=Path(__file__).resolve().parents[1]
WORK=BASE/'work';OUT=BASE/'output/expo-86-vector'

def masks(im):
 a=np.asarray(im).astype(float)
 r,g,b=a[:,:,:3].transpose(2,0,1)
 yy=np.arange(a.shape[0])[:,None]
 mm={
 'red':(r>1.65*g)&(r>1.55*b)&(r>80)&(yy<415),
 'blue':(b>1.35*r)&(b>1.18*g)&(b>70)&(yy>305)&(yy<808),
 'yellow':(r>1.02*g)&(g>95)&(g>1.7*b)&(yy>755)&(yy<1180),
 'green':(g>1.4*r)&(g>1.2*b)&(g>35)&(yy>1080)&(yy<1490)}
 for k,m in mm.items():
  lab,n=ndi.label(m)
  sizes=np.bincount(lab.ravel());sizes[0]=0
  m=lab==sizes.argmax()
  mm[k]=ndi.binary_fill_holes(m)
 return mm

def edge(mask):return mask ^ ndi.binary_erosion(mask)

def make_normalized():
 r=ET.parse(str(OUT/'Expo86_Vittorio_Reconstructed.svg'))
 root=r.getroot();root.set('width','1100px');root.set('height','1600px');root.set('viewBox','0 0 1100 1600')
 root.xpath('//*[@id="design"]')[0].attrib.pop('transform',None)
 r.write(str(WORK/'reconstruction-normalized.svg'))
 subprocess.run(['inkscape',str(WORK/'reconstruction-normalized.svg'),'--export-type=png','--export-filename='+str(WORK/'reconstruction-normalized.png'),'--export-width=1100'],check=True,capture_output=True)

def main():
 make_normalized()
 ref=Image.open(WORK/'reference-rectified.png').convert('RGB')
 rec=Image.open(WORK/'reconstruction-normalized.png').convert('RGB')
 rm,vm=masks(ref),masks(rec)
 metrics={}
 overlay=np.array(ref).copy()
 # A light photographic background with high-contrast contour annotations.
 contour=(np.array(ref,dtype=float)*.40+255*.60).astype(np.uint8)
 diff=np.full((1600,1100,3),246,dtype=np.uint8)
 for k in rm:
  a,b=rm[k],vm[k]
  ea,eb=edge(a),edge(b)
  da,db=ndi.distance_transform_edt(~ea),ndi.distance_transform_edt(~eb)
  d=np.r_[da[eb],db[ea]]
  metrics[k]={'intersection_over_union':float((a&b).sum()/(a|b).sum()),
              'mean_symmetric_boundary_distance_px':float(d.mean()),
              'p95_symmetric_boundary_distance_px':float(np.percentile(d,95)),
              'max_symmetric_boundary_distance_px':float(d.max()),
              'reference_area_px':int(a.sum()),'vector_area_px':int(b.sum())}
  contour[ndi.binary_dilation(ea,iterations=1)]=[0,160,186]
  contour[eb]=[224,0,113]
  diff[a&b]=[52,59,62];diff[a&~b]=[0,160,186];diff[b&~a]=[224,0,113]
  overlay[eb]=[248,0,151]
 Image.fromarray(overlay).save(WORK/'reference-vector-overlay.png')
 Image.fromarray(contour).save(WORK/'contour-comparison.png')
 Image.fromarray(diff).save(WORK/'silhouette-difference.png')
 Image.blend(ref,rec,.5).save(WORK/'fifty-percent-overlay.png')
 (WORK/'geometry-metrics.json').write_text(json.dumps(metrics,indent=2))
 print(json.dumps(metrics,indent=2))
 # Diagnostic strips: each makes the largest outline differences inspectable.
 for k,box in {'red':(0,0,1100,410),'blue':(0,315,1100,810),'yellow':(0,760,1100,1180),'green':(0,1080,1100,1490)}.items():
  Image.fromarray(contour).crop(box).save(WORK/f'contours-{k}.png')

if __name__=='__main__':main()
