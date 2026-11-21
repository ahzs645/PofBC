#!/usr/bin/env python3
"""Fixed-reference Revision 3/4 paint analysis; no diagnostic contours enter artwork.

Run from the workspace. A portable copy is provided in the delivered source folder.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
from xml.etree import ElementTree as ET
import numpy as np
from scipy.ndimage import gaussian_filter, binary_erosion, distance_transform_edt
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REV = ROOT / 'review'
OUT = ROOT
REF = ROOT / 'review/Reference_Perspective_Normalized.png'
MASK = ROOT / 'review/diagnostics/revision4/fixed-paint-mask.png'
PREV = ROOT / 'review/history/revision3'
DIAG = ROOT / 'review/diagnostics/revision4'

REGIONS = [
 ('All eligible paint', (0,0,1000,1400)),
 ('Upper-left paint pull', (15,240,185,515)),
 ('Central paint mass', (430,290,745,700)),
 ('Lower central stroke', (540,690,760,1015)),
 ('Quiet yellow field', (180,200,290,470)),
 ('Right paint band', (870,70,995,1110)),
 ('Lower paint / scumbles', (90,890,520,1015)),
]
TEAL = (0,182,190)
MAGENTA = (219,34,142)
INK = '#202a2b'
PAPER = '#faf9f3'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def render(svg, png):
 subprocess.run(['inkscape', str(svg), '--export-type=png', '--export-width=1000', '--export-filename='+str(png)], check=True, capture_output=True)

def vector_crop(svg,box,width,name):
 tree=ET.parse(svg);root=tree.getroot();x0,y0,x1,y1=box
 root.set('viewBox',f'{x0} {y0} {x1-x0} {y1-y0}')
 root.set('width',str(width));root.set('height',str(round(width*(y1-y0)/(x1-x0))))
 path=DIAG/(name+'.svg');png=DIAG/(name+'.png')
 tree.write(path,encoding='utf-8',xml_declaration=True)
 subprocess.run(['inkscape',str(path),'--export-type=png','--export-filename='+str(png)],check=True,capture_output=True)
 return Image.open(png).convert('RGB')

def rgb(path):
 return np.asarray(Image.open(path).convert('RGB'), dtype=float)

def font(n, bold=False):
 return ImageFont.truetype(BOLD if bold else FONT, n)

def mask_smooth(a, mask, sigma):
 weights=gaussian_filter(mask.astype(float), sigma)
 return np.stack([gaussian_filter(a[...,c]*mask,sigma)/np.maximum(weights,1e-12) for c in range(3)],axis=-1)

def orange(a):
 return gaussian_filter(a[...,1]/np.maximum(a[...,0],1),6)<.50

def iou(a,b,m):
 union=np.count_nonzero((a|b)&m)
 return float(np.count_nonzero(a&b&m)/union) if union else None

def text_wrap(draw, text, xy, font_obj, max_width, line_height, fill=INK):
 x,y=xy; line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if draw.textlength(candidate,font=font_obj)>max_width and line:
   draw.text((x,y),line,font=font_obj,fill=fill);y+=line_height;line=word
  else: line=candidate
 if line: draw.text((x,y),line,font=font_obj,fill=fill);y+=line_height
 return y

def diagnostic(photo, photo_orange, art_orange, mask):
 gray=np.mean(photo,axis=-1,keepdims=True)
 a=np.repeat(gray,3,axis=-1)*.48+np.array([241,241,235])*.52
 missing=photo_orange&~art_orange&mask
 extra=art_orange&~photo_orange&mask
 a[missing]=TEAL;a[extra]=MAGENTA
 return Image.fromarray(np.uint8(np.clip(a,0,255))),missing,extra

def main():
 DIAG.mkdir(parents=True,exist_ok=True)
 OUT.mkdir(parents=True,exist_ok=True)
 # Render the actual delivered components, not a lower-resolution screenshot.
 render(PREV/'BCFS_Paint_Background.svg', DIAG/'paint-v3.png')
 render(OUT/'BCFS_Paint_Background.svg', DIAG/'paint-v4.png')
 render(OUT/'BCFS_Matches_Reconstructed.svg', DIAG/'master-v4.png')
 render(PREV/'BCFS_Matches_Reconstructed.svg', DIAG/'master-v3.png')
 p=rgb(REF); old=rgb(DIAG/'paint-v3.png');new=rgb(DIAG/'paint-v4.png')
 m=np.asarray(Image.open(MASK).convert('L'))>127
 assert p.shape==old.shape==new.shape==(1400,1000,3)
 assert int(m.sum())==698156, 'Fixed paint mask changed; investigate rather than silently recomputing it.'
 masks={k:orange(v) for k,v in [('reference',p),('previous',old),('revised',new)]}
 smooth={s:{k:mask_smooth(a,m,s) for k,a in [('reference',p),('previous',old),('revised',new)]} for s in [8,24]}
 rows={}
 for name,(x0,y0,x1,y1) in REGIONS:
  region=m.copy();region[:y0]=False;region[y1:]=False;region[:,:x0]=False;region[:,x1:]=False
  row={'box':[x0,y0,x1,y1],'eligible_pixels':int(region.sum())}
  for key,a in [('previous',old),('revised',new)]:
   row[key]={'mean_absolute_rgb_error':float(np.mean(np.abs(a[region]-p[region]))),
             'broad_orange_iou':iou(masks['reference'],masks[key],region),
             'broad_orange_missing_pixels':int(np.count_nonzero(masks['reference']&~masks[key]&region)),
             'broad_orange_excess_pixels':int(np.count_nonzero(~masks['reference']&masks[key]&region))}
   for s in [8,24]: row[key][f'masked_smooth_rgb_error_sigma_{s}']=float(np.mean(np.abs(smooth[s][key][region]-smooth[s]['reference'][region])))
  rows[name]=row
 metrics={'revision':4,'previous_revision':3,'comparison_plane':[1000,1400],
          'fixed_mask_pixels':int(m.sum()),'fixed_mask_sha256':hashlib.sha256(MASK.read_bytes()).hexdigest(),
          'evaluated_paint_sha256':{'v3':hashlib.sha256((PREV/'BCFS_Paint_Background.svg').read_bytes()).hexdigest(),'v4':hashlib.sha256((OUT/'BCFS_Paint_Background.svg').read_bytes()).hexdigest()},
          'method':{'raw_error':'Mean absolute difference in 8-bit display RGB channels, eligible pixels only.',
                    'broad_orange':'Gaussian sigma 6 px of G / max(R, 1), classified orange when below 0.50; evaluated on identical V2 mask.',
                    'smoothed_error':'Gaussian normalized convolution of RGB through the fixed paint mask at sigma 8 or 24 px. Non-paint photo pixels are excluded before smoothing.'},
          'regions':rows,
          'limits':['Same photograph used for design fitting and evaluation: residuals are not held-out validation.',
                    'Thresholded orange overlap measures broad colour-field placement, not paint-material authenticity.',
                    'Pixel units belong to the estimated 1000 by 1400 registration plane, not original print dimensions.',
                    'Newly authored texture does not reproduce the exact historic grain; colour has not been physically calibrated.']}
 (DIAG/'Paint_Measurements.json').write_text(json.dumps(metrics,indent=2)+'\n')
 Image.fromarray(np.uint8(m)*255).save(DIAG/'fixed-paint-mask.png')
 overlays={}
 for key in ['previous','revised']:
  o,missing,extra=diagnostic(p,masks['reference'],masks[key],m)
  o.save(DIAG/f'paint-overlay-{key}.png');overlays[key]=o
  Image.fromarray(np.uint8(masks[key]&m)*255).save(DIAG/f'orange-mask-{key}.png')
 Image.fromarray(np.uint8(masks['reference']&m)*255).save(DIAG/'orange-mask-reference.png')
 ref=Image.open(REF).convert('RGB');v3=Image.open(DIAG/'master-v3.png').convert('RGB');v4=Image.open(DIAG/'master-v4.png').convert('RGB')
 # Recompute the complete joint record from these exact final masters. This
 # keeps portable reanalysis honest after any later editing of the artwork.
 joint_regions={'local_joint':[320,763,354,804], 'fracture_and_splinters':[325,766,345,799], 'context':[307,758,372,826]}
 joint_results={}
 for threshold in [90,110,125,140]:
  ink_masks={'reference':p.max(axis=-1)<threshold,'v3':np.asarray(v3).max(axis=-1)<threshold,'v4':np.asarray(v4).max(axis=-1)<threshold}
  edges={k:a&~binary_erosion(a) for k,a in ink_masks.items()}
  distances={k:distance_transform_edt(~e) for k,e in edges.items()}
  values={}
  for name,box in joint_regions.items():
   x0,y0,x1,y1=box;scope=np.zeros(m.shape,dtype=bool);scope[y0:y1,x0:x1]=True
   row={'bounds':box};r=ink_masks['reference']&scope
   for key in ['v3','v4']:
    c=ink_masks[key]&scope;ds=np.r_[distances['reference'][edges[key]&scope],distances[key][edges['reference']&scope]]
    row[key]={'iou':float((r&c).sum()/(r|c).sum()),'dice':float(2*(r&c).sum()/(r.sum()+c.sum())),
              'mean_symmetric_edge_distance':float(ds.mean()),'edge_distance_p95':float(np.quantile(ds,.95)),
              'excess_ink_pixels':int((c&~r).sum()),'missing_ink_pixels':int((r&~c).sum())}
   values[name]=row
  joint_results[str(threshold)]=values
 joint_record={'registration':'Existing 1000 x 1400 perspective-normalized photograph, unchanged for both versions.',
               'mask':'Dark ink classified by max(R,G,B) < threshold. Main threshold 125; 90/110/140 are fixed sensitivity checks. Masks are QA only, not construction data.',
               'units':'Normalized source pixels; not physical print size or authenticity.',
               'evaluated_master_sha256':{'v3':hashlib.sha256((PREV/'BCFS_Matches_Reconstructed.svg').read_bytes()).hexdigest(),'v4':hashlib.sha256((OUT/'BCFS_Matches_Reconstructed.svg').read_bytes()).hexdigest()},
               'thresholds':joint_results}
 (DIAG/'joint-metrics.json').write_text(json.dumps(joint_record,indent=2)+'\n')
 # A separate local ink diagnostic avoids confusing paint residuals with the crack.
 local=np.zeros(m.shape,dtype=bool);local[758:826,307:372]=True
 photo_ink=p.max(axis=-1)<125
 for key,im in [('previous',v3),('revised',v4)]:
  art_ink=np.asarray(im).max(axis=-1)<125
  o,_,_=diagnostic(p,photo_ink,art_ink,local)
  o.save(DIAG/f'ink-overlay-{key}.png')
 # Full artwork comparison.
 b=Image.new('RGB',(1656,910),PAPER);d=ImageDraw.Draw(b)
 d.text((28,20),'PAINT AND BROKEN MATCH — REVISION 4',font=font(27,True),fill=INK)
 for i,(name,im) in enumerate([('Registered photograph',ref),('Previous vector · Revision 3',v3),('Revised vector · Revision 4',v4)]):
  x=28+i*544;d.text((x,67),name,font=font(20,True),fill=INK);b.paste(im.resize((512,717),Image.Resampling.LANCZOS),(x,105))
 text_wrap(d,'Shared 1000 × 1400 comparison plane. Paint and the child’s broken hip junction change in this pass. White reserve, lettering and seal retain their previous construction.',(28,845),font(18),1590,26)
 b.save(OUT/'BCFS_Reconstruction_Comparison.png')
 # Broad orange-field diagnostics, with the photo as a common visual anchor.
 b=Image.new('RGB',(1656,1070),PAPER);d=ImageDraw.Draw(b)
 d.text((28,20),'PAINT OVERLAY — COLOUR-FIELD PLACEMENT',font=font(27,True),fill=INK)
 for i,(name,im) in enumerate([('Registered photograph',ref),('V3 · orange-field mismatch',overlays['previous']),('V4 · orange-field mismatch',overlays['revised'])]):
  x=28+i*544;d.text((x,67),name,font=font(20,True),fill=INK);b.paste(im.resize((512,717),Image.Resampling.LANCZOS),(x,105))
 d.rectangle((28,850,50,872),fill=TEAL);d.text((61,846),'Orange field in photo only',font=font(20),fill=INK)
 d.rectangle((655,850,677,872),fill=MAGENTA);d.text((688,846),'Orange field in vector only',font=font(20),fill=INK)
 a=rows['All eligible paint']['previous'];z=rows['All eligible paint']['revised']
 y=text_wrap(d,f"Broad orange overlap: {a['broad_orange_iou']:.1%} → {z['broad_orange_iou']:.1%}. Mean RGB fit residual: {a['mean_absolute_rgb_error']:.2f} → {z['mean_absolute_rgb_error']:.2f} levels per channel.",(28,895),font(21,True),1590,30)
 text_wrap(d,'The fixed mask excludes illustration, lettering, seal and their immediate edges. Colours highlight placement disagreement after broad smoothing; they do not score grain or prove an exact historical reconstruction. White and ink geometry are assessed separately.',(28,y+13),font(18),1590,27)
 b.save(OUT/'BCFS_Paint_Overlay.png')
 # Enlarged, uncropped-aspect paint studies with three fixed crops.
 crops=[('Central overlapping paint pulls',(470,390,760,780)),('Paint beneath the legs',(170,860,480,1015)),('Right-hand yellow / amber field',(850,670,1000,1000))]
 # Variable row height is proportional to each shared crop; no image stretching.
 rowsizes=[(430,520),(490,240),(145,460)]
 b=Image.new('RGB',(1656,1760),PAPER);d=ImageDraw.Draw(b)
 d.text((28,20),'PAINT DETAILS — PHOTO / PREVIOUS / REVISED',font=font(26,True),fill=INK)
 for i,title in enumerate(['Photograph','Revision 3','Revision 4']):d.text((28+i*544,65),title,font=font(21,True),fill=INK)
 y=108
 for (name,box),(targetw,rowh) in zip(crops,rowsizes):
  d.text((28,y),name,font=font(20,True),fill=INK);y+=37
  maxh=rowh
  for i,im in enumerate([ref,v3,v4]):
   c=im.crop(box);scale=min(512/c.width,maxh/c.height);c=c.resize((round(c.width*scale),round(c.height*scale)),Image.Resampling.LANCZOS)
   b.paste(c,(28+i*544+(512-c.width)//2,y))
  y+=maxh+25
 text_wrap(d,'The artwork uses composed vector fields and newly authored paint marks. The photograph is retained only as comparison evidence; it is not embedded in the SVG or PDF.',(28,y),font(18),1590,27)
 # Avoid empty lower space if row sizes change.
 b.crop((0,0,1656,min(1760,y+90))).save(OUT/'BCFS_Paint_Details.png')
 # The fracture proof uses the exact final master; vector is rendered at crop
 # scale, while the photograph is enlarged without inventing detail.
 box=(307,758,372,826);cw,ch=585,612
 crops=[ref.crop(box).resize((cw,ch),Image.Resampling.LANCZOS),
        vector_crop(PREV/'BCFS_Matches_Reconstructed.svg',box,cw,'crack-v3-final-proof'),
        vector_crop(OUT/'BCFS_Matches_Reconstructed.svg',box,cw,'crack-v4-final-proof')]
 b=Image.new('RGB',(1851,790),PAPER);d=ImageDraw.Draw(b)
 d.text((24,19),'BROKEN MATCH JUNCTION — STRUCTURE AND SPLINTERS',font=font(27,True),fill=INK)
 for i,(name,im) in enumerate(zip(['PHOTOGRAPH','REVISION 3','REVISION 4'],crops)):
  x=24+i*609;d.text((x,61),name,font=font(20,True),fill=INK);b.paste(im,(x,95))
 text_wrap(d,'The broad divider is replaced by an irregular split, a torn upper shoulder and tapered splinters. All views use the same crop and registration; vector views render directly from the delivered master files.',(24,728),font(19),1800,27)
 b.save(OUT/'BCFS_Child_Crack_Details.png')
 b=Image.new('RGB',(1290,845),PAPER);d=ImageDraw.Draw(b)
 d.text((24,18),'CHILD HIP — LOCAL INK OVERLAY',font=font(27,True),fill=INK)
 for i,key in enumerate(['previous','revised']):
  x=24+i*633;d.text((x,62),'REVISION 3' if i==0 else 'REVISION 4',font=font(21,True),fill=INK)
  im=Image.open(DIAG/f'ink-overlay-{key}.png').crop(box).resize((585,612),Image.Resampling.NEAREST)
  b.paste(im,(x,100))
 d.rectangle((24,734,44,754),fill=TEAL);d.text((54,729),'Ink in photo only',font=font(20),fill=INK)
 d.rectangle((657,734,677,754),fill=MAGENTA);d.text((687,729),'Ink in vector only',font=font(20),fill=INK)
 text_wrap(d,'Fixed dark-ink threshold: max(R,G,B) < 125. Enlarged pixel overlay; small slivers may reflect photo blur, print wear, threshold choice or registration. See the report for threshold sensitivity.',(24,772),font(18),1220,25)
 b.save(OUT/'BCFS_Child_Crack_Overlay.png')
 print(json.dumps(metrics['regions']['All eligible paint'],indent=2))

if __name__=='__main__': main()
