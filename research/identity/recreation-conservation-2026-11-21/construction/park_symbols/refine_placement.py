"""Refine affine placement of already hand-built pictograms within fixed circles.
This changes only position, orientation and overall x/y proportions; it never
extracts image contours or changes the authored component silhouettes.
"""
from pathlib import Path
import runpy,io,json,math
import numpy as np,cv2,cairosvg
from PIL import Image
from scipy import optimize
P=Path(__file__).resolve().parent
data=runpy.run_path(str(P/'build_park_symbols.py'))
yy,xx=np.mgrid[:200,:200];mask=(xx-99.5)**2+(yy-99.5)**2<88**2
out={}
for item in data['items']:
 key=item['id'][3:];body=data['art'][key]
 s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'+body+'</svg>'
 pix=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(),output_width=400,output_height=400))).convert('RGBA')
 a=np.array(pix.getchannel('A').resize((200,200),Image.Resampling.LANCZOS))/255.
 b=1-np.asarray(Image.open(P/'sources'/f'{item["id"]}.png').convert('L').resize((200,200),Image.Resampling.LANCZOS))/255.
 b*=mask;b=cv2.GaussianBlur(b,(3,3),.45)
 def matrix(v):
  sx,sy,tx,ty,ang=v;t=math.radians(ang);m=np.array([[math.cos(t)*sx,-math.sin(t)*sy],[math.sin(t)*sx,math.cos(t)*sy]])
  d=np.array([100+tx,100+ty])-m@np.array([100.,100.]);return np.column_stack([m,d]).astype('float32')
 def loss(v):
  q=cv2.warpAffine(a,matrix(v),(200,200),flags=cv2.INTER_LINEAR)
  if key=='sani_station':
   # This sign deliberately has a ground field meeting the circle.
   return np.mean(((q-b)**2)[mask])
  # Penalise stray reconstructed ink outside the sign interior. Ignoring it
  # would allow a fitted hanger or tent to grow into the circular border.
  return np.mean((q-b)**2)
 opt=optimize.minimize(loss,[1,1,0,0,0],method='Powell',bounds=[(.8,1.2),(.8,1.2),(-10,10),(-10,10),(-4,4)],options={'maxiter':80,'xtol':.0003,'ftol':1e-7})
 m=matrix(opt.x);out[key]={'parameters':dict(zip(['scale_x','scale_y','translation_x','translation_y','rotation_degrees'],map(float,opt.x))),'svg_matrix':list(map(float,[m[0,0],m[1,0],m[0,1],m[1,1],m[0,2],m[1,2]])),'initial_mse':float(loss([1,1,0,0,0])),'refined_mse':float(opt.fun),'method':'Affine placement refinement of authored primitive/cubic components; circular frame remains fixed.'}
 print(key,round(out[key]['initial_mse'],4),'->',round(opt.fun,4),flush=True)
(P/'placement_refinement.json').write_text(json.dumps(out,indent=2))
