import sys,numpy as np; sys.path.insert(0,'.')
from sfcommon import render, ink
from textpath import text_d
from PIL import Image, ImageFilter
from scipy.optimize import minimize
def blurred(m,b): return np.array(Image.fromarray((np.clip(m,0,1)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(b))).astype(float)/255
def bbox_of_mask(m):
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]; return xs.min(),ys.min(),xs.max()+1,ys.max()+1
def fit_text(target, region, font, text, blur=1.5, fix_tracking=None, extra_stroke=0.0, size=100.0):
    """target: ink 0..1 HxW. region: px box containing exactly this text. Returns dict with s,tx,ty,tracking."""
    H,W=target.shape
    x0,y0,x1,y1=region
    T=blurred(target,blur)
    sub=target[y0:y1,x0:x1]>0.5; bx0,by0,bx1,by1=bbox_of_mask(sub); bx0+=x0;bx1+=x0;by0+=y0;by1+=y0
    d,w=text_d(font,text,size)
    # initial guess from rendered bbox
    a=render(f'<g transform="translate(10 {size*1.2})"><path d="{d}"/></g>',int(w+40),int(size*2))
    gx0,gy0,gx1,gy1=bbox_of_mask(ink(a)>0.5)
    s0=(bx1-bx0)/(gx1-gx0); tx0=bx0-(gx0-10)*s0; ty0=by0-(gy0-size*1.2)*s0
    pad=6; cx0,cy0,cx1,cy1=max(0,x0-pad),max(0,y0-pad),min(W,x1+pad),min(H,y1+pad)
    def body(p):
        s,tx,ty,tr=p
        dd,_=text_d(font,text,size,tr)
        st=f' stroke="#000" stroke-width="{extra_stroke/s}" stroke-linejoin="round"' if extra_stroke else ''
        return f'<g transform="matrix({s} 0 0 {s} {tx} {ty})"><path d="{dd}" fill="#000"{st}/></g>'
    def loss(p):
        if fix_tracking is not None: p=list(p[:3])+[fix_tracking]
        R=blurred(ink(render(body(p),W,H)),blur)
        return ((R[cy0:cy1,cx0:cx1]-T[cy0:cy1,cx0:cx1])**2).sum()
    p0=[s0,tx0,ty0,0.0] if fix_tracking is None else [s0,tx0,ty0]
    simplex=[p0]+[[v*(1.02 if i==0 else 1)+(2 if i in(1,2) else 0)+(1.0 if i==3 else 0) if j==i else v for j,v in enumerate(p0)] for i in range(len(p0))]
    r=minimize(loss,p0,method='Nelder-Mead',options={'maxiter':600,'xatol':1e-3,'fatol':1e-2,'initial_simplex':simplex})
    p=list(r.x)+([fix_tracking] if fix_tracking is not None else [])
    return {'s':p[0],'tx':p[1],'ty':p[2],'tracking':p[3],'loss':float(r.fun),'body':body(p)}
