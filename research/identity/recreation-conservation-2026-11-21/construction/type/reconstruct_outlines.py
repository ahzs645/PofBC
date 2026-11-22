"""Analytical outline reconstruction from public type specimens.

Contours are measured at the antialias midline, segmented at actual corners,
and rebuilt as exact straight runs or smooth cubic Bezier segments. This
produces compact, reusable glyph components rather than bitmap scan tracing.
No font binary is used or produced.
"""
from pathlib import Path
import json,math,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from skimage.measure import find_contours
from scipy.ndimage import distance_transform_edt
import cairosvg
P=Path(__file__).resolve().parent
EM=256*4/3;UNIT=1000/EM;BASELINE=298.

def normalize(v):
 l=np.linalg.norm(v);return v/l if l>1e-12 else np.array([1.,0.])
def bezier(p,t):
 t=np.asarray(t);return ((1-t)**3)[...,None]*p[0]+(3*(1-t)**2*t)[...,None]*p[1]+(3*(1-t)*t*t)[...,None]*p[2]+(t**3)[...,None]*p[3]
def param(points):
 u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];return u/u[-1] if u[-1] else np.linspace(0,1,len(points))
def generate(points,u,t1,t2):
 b0=(1-u)**3;b1=3*u*(1-u)**2;b2=3*u*u*(1-u);b3=u**3
 A=np.stack([b1[:,None]*t1,b2[:,None]*t2],axis=1)
 tmp=points-(b0+b1)[:,None]*points[0]-(b2+b3)[:,None]*points[-1]
 C=np.einsum('nac,nbc->ab',A,A);X=np.einsum('nac,nc->a',A,tmp)
 try:alpha=np.linalg.solve(C,X)
 except np.linalg.LinAlgError:alpha=np.zeros(2)
 seg=np.linalg.norm(points[-1]-points[0]);eps=1e-6*seg
 if np.any(alpha<eps) or np.any(alpha>seg*5):alpha[:]=seg/3
 return np.array([points[0],points[0]+t1*alpha[0],points[-1]+t2*alpha[1],points[-1]])
def reparam(points,u,b):
 q=bezier(b,u);d=3*np.diff(b,axis=0);dd=2*np.diff(d,axis=0)
 qp=(1-u)[:,None]**2*d[0]+2*((1-u)*u)[:,None]*d[1]+u[:,None]**2*d[2]
 qpp=(1-u)[:,None]*dd[0]+u[:,None]*dd[1]
 delta=q-points;den=np.sum(qp*qp+delta*qpp,axis=1)
 un=u-np.divide(np.sum(delta*qp,axis=1),den,out=np.zeros_like(u),where=np.abs(den)>1e-10)
 un=np.clip(un,0,1)
 return un if np.all(np.diff(un)>=0) else u
def line_error(points):
 v=points[-1]-points[0];length=np.linalg.norm(v)
 if length<1e-8:return 999
 unit=v/length;d=points-points[0];pr=d@unit
 if np.min(pr)<-.2 or np.max(pr)>length+.2:return 999
 return np.max(np.abs(d[:,0]*unit[1]-d[:,1]*unit[0]))
def fit(points,t1=None,t2=None,tolerance=.30,depth=0):
 if len(points)<2:return []
 if line_error(points)<.15:return [('L',points[-1])]
 if t1 is None:t1=normalize(points[min(4,len(points)-1)]-points[0])
 if t2 is None:t2=normalize(points[max(0,len(points)-5)]-points[-1])
 if len(points)==2 or depth>22:
  length=np.linalg.norm(points[-1]-points[0])/3
  return [('C',np.array([points[0]+t1*length,points[-1]+t2*length,points[-1]]))]
 u=param(points);b=generate(points,u,t1,t2)
 for j in range(5):
  errors=np.sum((bezier(b,u)-points)**2,axis=1);split=int(np.argmax(errors));err=errors[split]
  if err<=tolerance*tolerance:return [('C',b[1:])]
  if err>tolerance*tolerance*16:break
  u=reparam(points,u,b);b=generate(points,u,t1,t2)
 split=max(1,min(len(points)-2,split));center=normalize(points[split-1]-points[split+1])
 return fit(points[:split+1],t1,center,tolerance,depth+1)+fit(points[split:],-center,t2,tolerance,depth+1)
def resample(points,step=.5):
 if np.linalg.norm(points[0]-points[-1])<1e-5:points=points[:-1]
 closed=np.vstack([points,points[0]]);u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(closed,axis=0),axis=1))]
 t=np.linspace(0,u[-1],max(8,round(u[-1]/step)),endpoint=False)
 return np.column_stack([np.interp(t,u,closed[:,0]),np.interp(t,u,closed[:,1])])
def corners(points):
 n=len(points);k=6
 before=points-np.roll(points,k,axis=0);after=np.roll(points,-k,axis=0)-points
 cos=np.sum(before*after,axis=1)/(np.linalg.norm(before,axis=1)*np.linalg.norm(after,axis=1)+1e-12)
 angle=np.arccos(np.clip(cos,-1,1));idx=np.where(angle>np.deg2rad(52))[0]
 selected=[]
 for i in sorted(idx,key=lambda x:angle[x],reverse=True):
  if all(min((i-j)%n,(j-i)%n)>9 for j in selected):selected.append(int(i))
 if len(selected)<2:
  selected=list(set([int(np.argmin(points[:,0])),int(np.argmax(points[:,0])),int(np.argmin(points[:,1])),int(np.argmax(points[:,1]))]))
 return sorted(selected)
def fnum(x):return f'{x:.3f}'.rstrip('0').rstrip('.')
def fmt(p):return ' '.join(fnum(float(v)*UNIT) for v in np.asarray(p).flatten())
def build_path(contour):
 pts=resample(contour);starts=corners(pts);n=len(pts);parts=[];nlines=0;ncurves=0
 parts.append('M'+fmt(pts[starts[0]]))
 for j,a in enumerate(starts):
  b=starts[(j+1)%len(starts)];segment=pts[a:b+1] if b>a else np.vstack([pts[a:],pts[:b+1]])
  for typ,coords in fit(segment):
   parts.append(typ+fmt(coords));nlines+=int(typ=='L');ncurves+=int(typ=='C')
 parts.append('Z');return ''.join(parts),nlines,ncurves

manifest=json.loads((P/'specimen_manifest.json').read_text());hh=manifest['items'][0];Horigin=hh['column_runs'][1][0]
glyphs={};metrics=[]
for item in manifest['items'][1:]:
 if 'error' in item:raise RuntimeError(item)
 c=item['char'];im=Image.open(P/item['path']).convert('L');a=np.array(im);runs=item['column_runs'];assert len(runs)==3,(c,runs)
 x0,x1=runs[1];left=max(0,x0-3);right=x1+3
 gray=a[:,left:right];alpha=1-gray/255.
 contours=find_contours(alpha,.5,fully_connected='high',positive_orientation='high')
 paths=[];nl=nc=0;allpoints=[]
 for cont in contours:
  if len(cont)<4:continue
  # Convert [row,column] to font-bearing x and baseline y.
  # skimage returns pixel-centre indices; SVG pixel centres are at n+0.5.
  pts=np.column_stack([cont[:,1]+.5+left-Horigin,cont[:,0]+.5-BASELINE])
  path,nline,ncurve=build_path(pts);paths.append(path);nl+=nline;nc+=ncurve;allpoints.append(pts)
 pts=np.vstack(allpoints);box=[pts[:,0].min()*UNIT,pts[:,1].min()*UNIT,pts[:,0].max()*UNIT,pts[:,1].max()*UNIT]
 advance=(runs[2][0]-Horigin)*UNIT
 glyphs[c]={'path':' '.join(paths),'advance':round(advance,6),'bbox':list(map(lambda v:round(float(v),6),box)),'source':item['path'],'line_segments':nl,'cubic_segments':nc,'contours':len(paths)}
 # Compare exact outline raster against the specimen at its native resolution.
 w,h=right-left,gray.shape[0]
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><g transform="translate({Horigin-left} {BASELINE}) scale({1/UNIT})" fill="black" fill-rule="evenodd"><path d="{glyphs[c]["path"]}"/></g></svg>'
 raw=cairosvg.svg2png(bytestring=svg.encode());vec=np.array(Image.open(io.BytesIO(raw)).convert('L'));srcmask=gray<128;vmask=vec<128
 union=np.sum(srcmask|vmask);iou=np.sum(srcmask&vmask)/union
 metrics.append({'character':c,'ink_iou_at_specimen_resolution':float(iou),'line_segments':nl,'cubic_segments':nc,'contours':len(paths)})
 ov=np.stack([255-srcmask.astype(float)*175,255-vmask.astype(float)*175,255-np.maximum(srcmask,vmask).astype(float)*75],axis=-1).astype('uint8')
 Image.fromarray(ov).save(P/'specimens'/f'overlay_u{ord(c):04x}.png')
 print(repr(c),'L',nl,'C',nc,'IoU',round(iou,4),flush=True)

(P/'glyph_geometry.json').write_text(json.dumps({'units_per_em':1000,'nominal_cap_height':625,'baseline':'y=0, positive y down','default_space':625,'status':'Restricted fixed-wording analytical reconstruction, not native font outlines or a font file.','method':'Public antialiased specimen contours at50% ink level; straight runs and smooth cubic curves fitted independently, shared glyph components reused for all branding wording.','glyphs':glyphs},indent=2))
(P/'outline_metrics.json').write_text(json.dumps({'glyphs':metrics,'mean_ink_iou':float(np.mean([m['ink_iou_at_specimen_resolution'] for m in metrics])),'reference':'Official public Corporatus raster specimens, rs256. IoU is rendering agreement, not historical authenticity.'},indent=2))

# Generate actual fixed-wording assets; each contains only curves and paths.
from type_engine import svg_text
(P/'wordmarks').mkdir(exist_ok=True)
for idx,phrase in enumerate(manifest['phrases']):
 tracking=-50 if phrase=='General Administration' else -22 if phrase=='Department of Recreation and Conservation' else -35
 ws=-220 if phrase=='General Administration' else -300 if phrase=='Department of Recreation and Conservation' else -260
 scale=.97 if phrase=='Department of Recreation and Conservation' else 1
 svg=svg_text(phrase,font_size=100,tracking=tracking,word_space=ws,horizontal_scale=scale,color='#163c36')
 filename=f'{idx+1:02d}_'+''.join(ch if ch.isalnum() else '_' for ch in phrase)+'.svg';(P/'wordmarks'/filename).write_text(svg)

# Glyph reconstruction inspection sheet, with the source/raster overlay.
W=1800;cellw=300;cellh=310;H=100+math.ceil(len(metrics)/6)*cellh
sheet=Image.new('RGB',(W,H),'#f4f1e8');draw=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
draw.text((30,20),'Corporatus-based outline reconstruction / fixed branding wording',font=fb,fill='#163c36')
draw.text((30,62),'Cyan: specimen. Pink: reconstructed paths. Dark overlap: agreement. No font software embedded.',font=f,fill='#52675e')
for i,m in enumerate(metrics):
 x=(i%6)*cellw;y=100+(i//6)*cellh;c=m['character'];pic=Image.open(P/'specimens'/f'overlay_u{ord(c):04x}.png')
 # Vertical crop retains complete glyph, independently scaled only for review.
 mask=np.array(pic).min(2)<220;yy,xx=np.where(mask);pic=pic.crop((xx.min(),yy.min(),xx.max()+1,yy.max()+1));pic.thumbnail((260,220),Image.Resampling.LANCZOS)
 sheet.paste(pic,(x+20+(260-pic.width)//2,y+45));draw.text((x+20,y+8),c,font=fb,fill='#163c36');draw.text((x+20,y+276),f'Ink overlap {m["ink_iou_at_specimen_resolution"]:.3f}',font=f,fill='#52675e')
sheet.save(P/'Glyph_Outline_Comparison.png')
