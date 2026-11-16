import sys, json, numpy as np
from PIL import Image, ImageFilter
from scipy.optimize import minimize
sys.path.insert(0,'.')
from sfcommon import *
def fit_groups(target_mask, regions, uniform_text_scale=False, blur=1.0):
    """target_mask: float HxW 0..1 ink. regions: {group:(x0,y0,x1,y1)} pixel bbox in target."""
    H,W=target_mask.shape
    T=np.array(Image.fromarray((target_mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(blur))).astype(float)/255
    res={}
    for g,(x0,y0,x1,y1) in regions.items():
        bx0,by0,bx1,by1=bbox(GROUPS[g])
        s0=((x1-x0)/(bx1-bx0)+(y1-y0)/(by1-by0))/2 if g!='rule' else (x1-x0)/(bx1-bx0)
        tx0=x0-bx0*s0; ty0=y0-by0*s0
        if g=='rule': ty0=(y0+y1)/2-by0*s0
        pad=8; cx0,cy0,cx1,cy1=max(0,int(x0)-pad),max(0,int(y0)-pad),min(W,int(x1)+pad),min(H,int(y1)+pad)
        body=group_svg(GROUPS[g])
        def loss(p):
            s,tx,ty=p
            a=render(f'<g transform="matrix({s} 0 0 {s} {tx} {ty})">{body}</g>',W,H)
            R=np.array(Image.fromarray(a).convert('L').filter(ImageFilter.GaussianBlur(blur))).astype(float)
            R=1-R/255
            return ((R[cy0:cy1,cx0:cx1]-T[cy0:cy1,cx0:cx1])**2).sum()
        best=minimize(loss,[s0,tx0,ty0],method='Nelder-Mead',options={'xatol':1e-3,'fatol':1e-3,'maxiter':400,'initial_simplex':[[s0,tx0,ty0],[s0*1.02,tx0,ty0],[s0,tx0+2,ty0],[s0,tx0,ty0+2]]})
        res[g]=list(map(float,best.x)); print(g,res[g],'init',[s0,tx0,ty0],'loss',best.fun,flush=True)
    return res
