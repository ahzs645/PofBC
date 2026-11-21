#!/usr/bin/env python3
"""Paint-only diagnostic analysis, separated from all vector construction.

This reads the supplied photo and the fixed V2 evaluation mask. It never writes
geometry and is not imported by the paint generator.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
from scipy.ndimage import gaussian_filter, binary_erosion
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
REV=HERE.parent
ROOT=REV.parents[1]
OUT=REV/'paint-analysis'
REGIONS={
 'All eligible paint':(0,0,1000,1400),
 'Upper-left paint pull':(15,240,185,515),
 'Central paint mass':(430,290,745,700),
 'Lower central stroke':(540,690,760,1015),
 'Quiet yellow field':(180,200,290,470),
 'Right paint band':(870,70,995,1110),
 'Lower paint and scumbles':(90,890,520,1015),
}

def font(n,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
def imarray(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)
def smooth(a,m,sigma):
 weights=gaussian_filter(m.astype(np.float32),sigma)
 return np.stack([gaussian_filter(a[:,:,c]*m,sigma)/np.maximum(weights,1e-6) for c in range(3)],2)
def heatmap(error,mask,maximum):
 value=np.clip(error/maximum,0,1)
 anchors=np.array([[250,248,232],[252,201,78],[232,112,40],[177,24,57],[73,18,65]],float)
 t=value*4;i=np.minimum(t.astype(int),3);r=anchors[i]*(1-(t-i)[...,None])+anchors[i+1]*(t-i)[...,None]
 r[~mask]=[228,230,225]
 return Image.fromarray(np.uint8(r))
def orange(a):return gaussian_filter(a[:,:,1]/np.maximum(a[:,:,0],1),6)<.5
def photo_overlay(photo,reference,candidate,m):
 out=photo*.27+np.array([244,243,235])*.73
 out[(reference&~candidate)&m]=[0,137,157]
 out[(candidate&~reference)&m]=[205,39,133]
 return Image.fromarray(np.uint8(out))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--candidate',type=Path,default=REV/'paint_v4_draft.png');parser.add_argument('--label',default='candidate')
 args=parser.parse_args();args.candidate=args.candidate.resolve();OUT.mkdir(exist_ok=True)
 photo=imarray(ROOT/'work/reference-rectified.png')
 old=imarray(OUT/'v3-paint.png');new=imarray(args.candidate)
 maskfile=ROOT/'work/revision2/background-evaluation-mask.png'
 mask=np.asarray(Image.open(maskfile).convert('L'))>127
 assert int(mask.sum())==698156
 images={'photo':photo,'v3':old,'v4':new};scaled={0:images}
 for sigma in [1.2,4,8,24,48]:scaled[sigma]={k:smooth(v,mask,sigma) for k,v in images.items()}
 orange_masks={k:orange(v) for k,v in images.items()}
 report={'fixed_mask_pixels':int(mask.sum()),'fixed_mask_sha256':hashlib.sha256(maskfile.read_bytes()).hexdigest(),
         'candidate':str(args.candidate.relative_to(REV)),'regions':{},
         'method':{'comparison_plane':[1000,1400],
                   'rgb':'Mean absolute display-RGB channel difference on unchanged V2 paint mask.',
                   'scales':'Gaussian normalized convolution through the same paint mask; non-paint excluded before smoothing. Sigma 4,8,24,48 pixels.',
                   'orange':'Legacy Gaussian sigma6 on G/max(R,1), orange if below.50; identical fixed eligible-paint mask.',
                   'texture':'Green-channel bandpass, normalized-convolution sigma1.2 minus sigma8. RMS contrast and adjacent-pixel directional difference use the mask eroded four pixels. dx/dy above1 indicates more vertical structure; below1 more horizontal structure.',
                   'limits':'Same reference is used for fitting and evaluation. Scores describe photo appearance, not historical authenticity, physical ink calibration or exact grain recovery.'}}
 validtex=binary_erosion(mask,iterations=4)
 for name,box in REGIONS.items():
  x0,y0,x1,y1=box;region=np.zeros_like(mask);region[y0:y1,x0:x1]=True;region&=mask
  row={'bounds':list(box),'eligible_pixels':int(region.sum())}
  for key,a in [('v3',old),('v4',new)]:
   d={'mean_absolute_rgb_error':float(np.abs(a-photo)[region].mean())}
   om=orange_masks[key];ref=orange_masks['photo'];d['broad_orange_iou']=float((om&ref&region).sum()/((om|ref)&region).sum()) if ((om|ref)&region).any() else None
   for sigma in [4,8,24,48]:d[f'masked_smooth_rgb_error_sigma_{sigma}']=float(np.abs(scaled[sigma][key]-scaled[sigma]['photo'])[region].mean())
   row[key]=d
  texscope=region&validtex
  for key in ['photo','v3','v4']:
   band=(scaled[1.2][key]-scaled[8][key])[:,:,1]
   mx=texscope[:,1:]&texscope[:,:-1];my=texscope[1:]&texscope[:-1]
   dx=float(np.mean(np.abs(np.diff(band,axis=1)[mx])));dy=float(np.mean(np.abs(np.diff(band,axis=0)[my])))
   row.setdefault(key,{})['texture_band_rms']=float(np.sqrt(np.mean(band[texscope]**2)))
   row[key]['texture_dx_over_dy']=dx/max(dy,1e-9)
  report['regions'][name]=row
 (OUT/(args.label+'-metrics.json')).write_text(json.dumps(report,indent=2))
 print(json.dumps(report['regions']['All eligible paint'],indent=2))
 for sigma,maximum in [(0,65),(24,40)]:
  for key in ['v3','v4']:
   error=np.abs(scaled[sigma][key]-scaled[sigma]['photo']).mean(2)
   heatmap(error,mask,maximum).save(OUT/f'{args.label}-{key}-error-sigma{sigma}.png')
 for key in ['v3','v4']:
  photo_overlay(photo,orange_masks['photo'],orange_masks[key],mask).save(OUT/f'{args.label}-{key}-orange-overlay.png')
 # One common colour scale for each pair, including its explicit endpoints.
 board=Image.new('RGB',(1400,1130),'#f4f3ed');d=ImageDraw.Draw(board)
 d.text((24,18),'PAINT RESIDUALS · RAW AND BROAD FIELDS',font=font(25,True),fill='#20302c')
 for j,(sigma,maximum,label) in enumerate([(0,65,'Raw display-RGB residual'),(24,40,'Broad fields · masked Gaussian σ24')]):
  x=24+j*700;d.text((x,65),label,font=font(20,True),fill='#38544b')
  for i,key in enumerate(['v3','v4']):
   xx=x+i*338;d.text((xx,100),key.upper(),font=font(18,True),fill='#38544b')
   im=Image.open(OUT/f'{args.label}-{key}-error-sigma{sigma}.png').resize((315,441),Image.Resampling.LANCZOS)
   board.paste(im,(xx,134))
  d.text((x,590),f'Shared scale: 0–{maximum} RGB levels/channel; gray is excluded.',font=font(16),fill='#38544b')
 # A lower-belt bandpass shows directional structure without source colour bias.
 box=(90,890,520,1015);x0,y0,x1,y1=box
 d.text((24,656),'LOWER BELT · TEXTURE BAND (σ1.2 − σ8)',font=font(23,True),fill='#20302c')
 for i,key in enumerate(['photo','v3','v4']):
  band=(scaled[1.2][key]-scaled[8][key])[:,:,1]
  gray=np.uint8(np.clip(128+band*3,0,255));gray[~mask]=228
  im=Image.fromarray(gray).convert('RGB').crop(box).resize((430,125),Image.Resampling.BICUBIC)
  x=24+i*460;d.text((x,705),{'photo':'PHOTO','v3':'V3','v4':'V4'}[key],font=font(18,True),fill='#38544b');board.paste(im,(x,743))
 d.text((24,905),'Both the colour-field maps and the texture comparison use the unchanged paint-only mask.',font=font(20),fill='#20302c')
 d.text((24,942),'Photo masks are diagnostic inputs only; no photograph pixels generate the final vector paths.',font=font(18),fill='#53675f')
 d.text((24,979),'The source contains printing wear and camera blur. Fitted residuals are not a historical-fidelity score.',font=font(18),fill='#53675f')
 board.crop((0,0,1400,1045)).save(OUT/(args.label+'-multiscale-review.png'))

 # A preview retaining V3 foreground lets paint placement be read in context.
 fg=OUT/'v3-foreground.png'
 if not fg.exists():
  tree=ET.parse(REV/'prior/BCFS_Matches_Reconstructed.svg');ns={'s':'http://www.w3.org/2000/svg'}
  paint=tree.getroot().find('.//s:g[@id="painted-background"]',ns)
  for parent in tree.getroot().iter():
   if paint in list(parent):parent.remove(paint);break
  path=OUT/'v3-foreground.svg';tree.write(path,encoding='utf-8',xml_declaration=True)
  subprocess.run(['inkscape',str(path),'--export-width=1000','--export-filename='+str(fg)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 foreground=Image.open(fg).convert('RGBA');preview=Image.fromarray(np.uint8(new)).convert('RGBA');preview.alpha_composite(foreground);preview=preview.convert('RGB')
 preview.save(REV/'paint_v4_preview.png')
 prev=Image.open(REV/'prior/BCFS_Matches_Preview.png').convert('RGB').resize((1000,1400),Image.Resampling.LANCZOS)
 pic=Image.fromarray(np.uint8(photo))
 board=Image.new('RGB',(1660,880),'#f4f3ed');d=ImageDraw.Draw(board)
 d.text((25,18),'PAINT COMPOSITION · PHOTOGRAPH / V3 / V4',font=font(26,True),fill='#20302c')
 for i,(label,im) in enumerate([('PHOTOGRAPH',pic),('V3',prev),('V4 PAINT / V3 FOREGROUND',preview)]):
  x=25+i*550;d.text((x,64),label,font=font(18,True),fill='#38544b');board.paste(im.resize((510,714),Image.Resampling.LANCZOS),(x,105))
 board.save(OUT/(args.label+'-full-comparison.png'))
 for name,box,scale in [('central',(420,250,780,1015),1.5),('lower',(70,835,560,1015),2),('right',(870,100,995,1110),1),('quiet',(180,200,295,830),1.5)]:
  w=round((box[2]-box[0])*scale);h=round((box[3]-box[1])*scale);b=Image.new('RGB',(w*3+80,h+120),'#f4f3ed');dr=ImageDraw.Draw(b)
  for i,(label,im) in enumerate([('PHOTO',pic),('V3',prev),('V4',preview)]):
   x=20+i*(w+20);dr.text((x,18),label,font=font(19,True),fill='#38544b');b.paste(im.crop(box).resize((w,h),Image.Resampling.BICUBIC),(x,60))
  dr.text((20,h+80),'Same registered crop; V3 foreground retained for this paint review.',font=font(16),fill='#53675f')
  b.save(OUT/f'{args.label}-{name}-comparison.png')

if __name__=='__main__':main()
