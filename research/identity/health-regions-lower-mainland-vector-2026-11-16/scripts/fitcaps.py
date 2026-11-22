import sys,numpy as np; sys.path.insert(0,'.')
from fittext import *
def fit_caps(T, box, font, text, size=100.0, refine=True, blur=2.0):
    """box: tight px bbox of the set line (x0,y0,x1,y1) measured in the target. Uniform scale from height,
    tracking from width; then small Nelder-Mead refinement of (s,tx,ty,tracking)."""
    x0,y0,x1,y1=box
    d,w=text_d(font,text,size)
    a=render(f'<g transform="translate(20 {size*1.5})"><path d="{d}"/></g>',int(w+60),int(size*2),4)
    gx0,gy0,gx1,gy1=[v/4 for v in bbox_of_mask(ink(a)>0.5)]
    gx0-=20;gx1-=20;gy0-=size*1.5;gy1-=size*1.5
    s=(y1-y0)/(gy1-gy0)
    n=len(text)-1
    tr=((x1-x0)/s-(gx1-gx0))/max(n,1)
    tx=x0-gx0*s; ty=y0-gy0*s
    p=[s,tx,ty,tr]
    if refine:
        H,W=T.shape; Tb=blurred(T,blur)
        cx0,cy0,cx1,cy1=max(0,x0-10),max(0,y0-10),min(W,x1+10),min(H,y1+10)
        def body(p):
            dd,_=text_d(font,text,size,p[3]); return f'<g transform="matrix({p[0]} 0 0 {p[0]} {p[1]} {p[2]})"><path d="{dd}"/></g>'
        def loss(p):
            R=blurred(ink(render(body(p),W,H)),blur); return ((R[cy0:cy1,cx0:cx1]-Tb[cy0:cy1,cx0:cx1])**2).sum()
        p0=p
        r=minimize(loss,p0,method='Nelder-Mead',options={'maxiter':250,'initial_simplex':[p0,[p0[0]*1.01]+p0[1:],[p0[0],p0[1]+3]+p0[2:],[p0[0],p0[1],p0[2]+3,p0[3]],p0[:3]+[p0[3]+1]]})
        p=list(r.x); l=r.fun
    else: l=None
    return {'s':p[0],'tx':p[1],'ty':p[2],'tracking':p[3],'loss':l}
