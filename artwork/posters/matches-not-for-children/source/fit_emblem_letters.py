"""Fit existing font glyph transforms to the photographed seal (never trace contours)."""
from pathlib import Path
import math,json,os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates,label,center_of_mass,binary_dilation,gaussian_filter
from scipy.optimize import minimize
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parent
CANDIDATES=[ROOT/'reference-rectified.png',ROOT.parent/'reference-rectified.png',ROOT.parent/'review'/'Reference_Perspective_Normalized.png']
REFERENCE=Path(os.environ['BCFS_REFERENCE']).expanduser() if os.environ.get('BCFS_REFERENCE') else next((p for p in CANDIDATES if p.is_file()),CANDIDATES[0])
if not REFERENCE.is_file():
 raise FileNotFoundError('The optional fit analysis needs the normalized reference PNG. Set BCFS_REFERENCE or retain review/Reference_Perspective_Normalized.png beside the source directory.')
REF=np.asarray(Image.open(REFERENCE).convert('RGB')).astype(float)
LIGHT=np.clip((REF.max(2)-75)/85,0,1)
Y,X=np.mgrid[:1400,:1000]
ANNULUS=(((X-914.5)/60.5)**2+((Y-1217.5)/74.5)**2<1)&~(((X-914)/43)**2+((Y-1219.8)/58)**2<1)
LABELS,N=label((REF.max(2)>130)&ANNULUS)
COUNTS=np.bincount(LABELS.ravel())
CENTRES=center_of_mass(LABELS>0,LABELS,range(1,N+1))
COMPONENTS=[(i,c) for i,c in enumerate(CENTRES,1) if COUNTS[i]>25]
TOP=sorted([(i,c) for i,c in COMPONENTS if c[0]<1215],key=lambda item:math.atan2((item[1][0]-1217.5)/74.5,(item[1][1]-914.5)/60.5))
BOTTOM=sorted([(i,c) for i,c in COMPONENTS if c[0]>1215],key=lambda item:math.atan2((item[1][0]-1217.5)/74.5,(item[1][1]-914.5)/60.5),reverse=True)
assert len(TOP)==13 and len(BOTTOM)==15,(len(TOP),len(BOTTOM))
URW=Path(os.environ.get('BCFS_URW_FONT_DIR','/usr/share/fonts/opentype/urw-base35')).expanduser()
FONTS={
 'nimbus':str(URW/'NimbusRoman-Bold.otf'),
 'bookman':str(URW/'URWBookman-Demi.otf'),
 'bookman_light':str(URW/'URWBookman-Light.otf'),
 'c059':str(URW/'C059-Bold.otf'),
 'dejavu':os.environ.get('BCFS_DEJAVU_SERIF','/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'),
}

def anchors(fontpath,text,rx,ry,first,last,fontsize=54.5,widthscale=.97):
 f=TTFont(fontpath);cmap=f.getBestCmap();upm=f['head'].unitsPerEm
 t=np.linspace(math.radians(first),math.radians(last),6000)
 xx=210+rx*np.cos(t);yy=255+ry*np.sin(t);s=np.r_[0,np.cumsum(np.hypot(np.diff(xx),np.diff(yy)))]
 advances=[f['hmtx'][cmap[ord(ch)]][0]*fontsize/upm*widthscale for ch in text]
 spacing=(s[-1]-sum(advances))/(len(text)-1)
 p=0;direction=1 if last>first else -1;out=[]
 for i,(ch,adv) in enumerate(zip(text,advances)):
  th=np.interp(p+adv/2,s,t);x=210+rx*math.cos(th);y=255+ry*math.sin(th)
  dx=direction*-rx*math.sin(th);dy=direction*ry*math.cos(th);norm=math.hypot(dx,dy);u=dx/norm;v=dy/norm
  if ch!=' ':out.append({'ch':ch,'x':844.5+(x-u*adv/2)/3,'y':1132.5+(y-v*adv/2)/3,'angle':math.atan2(v,u),'em':fontsize/3,'ws':widthscale,'i':i})
  p+=adv+spacing
 return out

def fit_font(name,fontpath):
 items=anchors(fontpath,'FOREST SERVICE',135,174,-172,-8)+anchors(fontpath,'BRITISH COLUMBIA',174,226,174,6,widthscale=1.06)
 ft=ImageFont.truetype(fontpath,100)
 result=[];scores=[]
 for row,(component_id,centroid) in zip(items,TOP+BOTTOM):
  ch=row['ch'];im=Image.new('L',(150,150));ImageDraw.Draw(im).text((15,115),ch,font=ft,fill=255,anchor='ls');glyph=np.asarray(im).astype(float)/255
  nz=np.where(glyph>.1);lo=[nz[1].min()-15,115-nz[0].max()];hi=[nz[1].max()-15,115-nz[0].min()]
  th=row['angle'];u,v=math.cos(th),math.sin(th);size=row['em']/100
  corners=[(row['x']+u*size*row['ws']*x+v*size*y,row['y']+v*size*row['ws']*x-u*size*y) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]]]
  component=LABELS==component_id;iy,ix=np.where(component)
  x0=max(0,int(ix.min())-3);x1=min(1000,int(ix.max())+4)
  y0=max(0,int(iy.min())-3);y1=min(1400,int(iy.max())+4)
  yy,xx=np.mgrid[y0:y1,x0:x1]
  local_component=component[y0:y1,x0:x1]
  target=LIGHT[y0:y1,x0:x1]*binary_dilation(local_component,iterations=1)
  gy0,gx0=np.mgrid[:150,:150];mass=glyph.sum()
  gxbar=float((glyph*(gx0-15)).sum()/mass);gybar=float((glyph*(115-gy0)).sum()/mass)
  predx=row['x']+u*size*row['ws']*gxbar+v*size*gybar
  predy=row['y']+v*size*row['ws']*gxbar-u*size*gybar
  dx0=float(centroid[1]-predx);dy0=float(centroid[0]-predy)
  def render(q):
   dx,dy,da,sx,sy=q;angle=th+math.radians(da);uu,vv=math.cos(angle),math.sin(angle)
   px=xx-row['x']-dx;py=yy-row['y']-dy
   gx=(uu*px+vv*py)/(size*row['ws']*sx)+15;gy=115-(vv*px-uu*py)/(size*sy)
   return map_coordinates(glyph,[gy,gx],order=1,cval=0,mode='constant')
  def loss(q):
   vec=render(q)
   dice=2*(vec*target).sum()/max(1,(vec*vec).sum()+(target*target).sum())
   # Modest regularization preserves a coherent alphabet instead of chasing wear.
   reg=.002*((q[0]-dx0)**2+(q[1]-dy0)**2)+.00008*q[2]**2+.015*((q[3]-1)**2+(q[4]-1)**2)
   return 1-dice+reg
  fit=minimize(loss,[dx0,dy0,0,1,1],method='Powell',bounds=[(dx0-2.4,dx0+2.4),(dy0-2.4,dy0+2.4),(-9,9),(.62,1.16),(.75,1.13)],options={'maxiter':75,'xtol':.02,'ftol':.0001})
  row['fit']=[float(x) for x in fit.x];row['loss']=float(fit.fun);result.append(row);scores.append(1-fit.fun)
 print(name,round(float(np.mean(scores)),4),flush=True)
 return {'font':fontpath,'mean_fit_score':float(np.mean(scores)),'glyphs':result}

if __name__=='__main__':
 out={k:fit_font(k,v) for k,v in FONTS.items()}
 (ROOT/'letter_transform_fits.json').write_text(json.dumps(out,indent=2))
