"""Fit the white ridge and sun lines of the Coast Garibaldi symbol: centreline pixels of the June 2000
greyscale bitmap are skeletonised, split at their junctions, and each run is fitted with a smooth cubic
Bezier (Catmull-Rom through points sampled every ~10 px). Output: list of SVG path d strings in bitmap px."""
import numpy as np
from collections import deque
from PIL import Image
from skimage.morphology import skeletonize
def strokes(png, cx, cy, r):
    a=np.array(Image.open(png)).astype(float)[:, :290]
    yy,xx=np.mgrid[:a.shape[0],:a.shape[1]]
    w=(a>128)&(np.hypot(xx-cx,yy-cy)<r-2)&(yy<121)
    sk=skeletonize(w); pts=set(zip(*np.where(sk)))
    def nb(p): return [(p[0]+dy,p[1]+dx) for dy in (-1,0,1) for dx in (-1,0,1) if (dy or dx) and (p[0]+dy,p[1]+dx) in pts]
    def path(a_,b_):
        prev={a_:None}; q=deque([a_])
        while q:
            p=q.popleft()
            if p==b_: break
            for n in nb(p):
                if n not in prev: prev[n]=p; q.append(n)
        out=[];p=b_
        while p is not None: out.append(p); p=prev[p]
        return out[::-1]
    def near(rc): return min(pts,key=lambda p:(p[0]-rc[0])**2+(p[1]-rc[1])**2)
    E=lambda r_,c_: near((r_,c_))
    runs={
      'left_ridge':[E(96,34),E(95,128),E(120,152)],
      'upper_ridge':[E(95,128),E(70,146),E(47,202),E(44,233)],
      'sun':[E(70,146),E(30,175),E(47,202)],
      'right_ridge':[E(71,252),E(120,193)],
    }
    out={}
    for k,nodes in runs.items():
        seq=[]
        for a_,b_ in zip(nodes,nodes[1:]):
            p=path(a_,b_); seq+=p if not seq else p[1:]
        out[k]=np.array([(c,r_) for r_,c in seq],float)  # x,y
    return out, w.sum()/sk.sum()
def smooth_bezier(P, step=10, extend_start=0, extend_end=0):
    # resample by arclength
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]
    n=max(2,int(round(d[-1]/step)))
    s=np.linspace(0,d[-1],n+1)
    Q=np.c_[np.interp(s,d,P[:,0]),np.interp(s,d,P[:,1])]
    # light smoothing of interior points (pixel staircase)
    Qs=Q.copy(); Qs[1:-1]=(Q[:-2]+2*Q[1:-1]+Q[2:])/4
    if extend_start:
        v=Qs[0]-Qs[1]; Qs[0]=Qs[0]+v/np.hypot(*v)*extend_start
    if extend_end:
        v=Qs[-1]-Qs[-2]; Qs[-1]=Qs[-1]+v/np.hypot(*v)*extend_end
    f=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    d_=f'M {f(Qs[0,0])} {f(Qs[0,1])}'
    for i in range(len(Qs)-1):
        p0=Qs[max(i-1,0)];p1=Qs[i];p2=Qs[i+1];p3=Qs[min(i+2,len(Qs)-1)]
        c1=p1+(p2-p0)/6; c2=p2-(p3-p1)/6
        d_+=f' C {f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}'
    return d_
