"""Outline fitting for clean 1-bit artwork: contour at the 50% level of a lightly smoothed mask, split at
corners (turning angle > CORNER deg on a simplified polygon), straight runs kept as lines, curved runs fitted
with least-squares cubic Beziers (Schneider's algorithm, max error MAXERR px). Disclosed as bitmap-contour fitting."""
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import find_contours
def rdp(P,eps):
    if len(P)<3: return [0,len(P)-1]
    a,b=P[0],P[-1]; ab=b-a; L=np.hypot(*ab)
    d=np.abs(ab[0]*(P[:,1]-a[1])-ab[1]*(P[:,0]-a[0]))/L if L>0 else np.hypot(*(P-a).T)
    i=int(np.argmax(d))
    if d[i]>eps:
        l=rdp(P[:i+1],eps); r=rdp(P[i:],eps); return l[:-1]+[x+i for x in r]
    return [0,len(P)-1]
def bez(p,t):
    t=t[:,None]; return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t**2*p[2]+t**3*p[3]
def fit_cubic(P,t1,t2,maxerr,depth=0):
    if len(P)==2:
        d=np.hypot(*(P[1]-P[0]))/3; return [[P[0],P[0]+t1*d,P[1]+t2*d,P[1]]]
    u=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; u/=u[-1]
    def gen(u):
        A1=3*(1-u)**2*u; A2=3*(1-u)*u**2
        C=np.zeros((2,2)); X=np.zeros(2)
        a1=A1[:,None]*t1; a2=A2[:,None]*t2
        C[0,0]=(a1*a1).sum(); C[0,1]=C[1,0]=(a1*a2).sum(); C[1,1]=(a2*a2).sum()
        tmp=P-bez(np.array([P[0],P[0],P[-1],P[-1]]),u)
        X[0]=(a1*tmp).sum(); X[1]=(a2*tmp).sum()
        det=C[0,0]*C[1,1]-C[0,1]**2
        seg=np.hypot(*(P[-1]-P[0]))
        if abs(det)<1e-12: al=be=seg/3
        else:
            al=(X[0]*C[1,1]-X[1]*C[0,1])/det; be=(C[0,0]*X[1]-C[0,1]*X[0])/det
        if al<1e-6*seg or be<1e-6*seg: al=be=seg/3
        return np.array([P[0],P[0]+t1*al,P[-1]+t2*be,P[-1]])
    for it in range(6):
        b=gen(u); e=np.hypot(*(bez(b,u)-P).T); i=int(np.argmax(e))
        if e[i]<maxerr: return [b]
        # reparameterise (Newton)
        q=bez(b,u); d1=3*((1-u)[:,None]**2*(b[1]-b[0])+2*((1-u)*u)[:,None]*(b[2]-b[1])+(u**2)[:,None]*(b[3]-b[2]))
        d2=6*((1-u)[:,None]*(b[2]-2*b[1]+b[0])+u[:,None]*(b[3]-2*b[2]+b[1]))
        num=((q-P)*d1).sum(1); den=(d1*d1).sum(1)+((q-P)*d2).sum(1)
        u=np.clip(u-np.where(np.abs(den)>1e-9,num/den,0),0,1); u[0]=0;u[-1]=1; u=np.maximum.accumulate(u)
    if len(P)<4 or depth>12: return [b]
    i=max(1,min(len(P)-2,i))
    tc=P[i-1]-P[i+1]; tc/=np.hypot(*tc) or 1
    return fit_cubic(P[:i+1],t1,tc,maxerr,depth+1)+fit_cubic(P[i:],-tc,t2,maxerr,depth+1)
def unit(v): n=np.hypot(*v); return v/n if n else v
def fit_contour(C, corner=50, maxerr=1.0, simplify=1.2, straight=0.6, smooth=1):
    """C: closed contour points (x,y) with C[0]==C[-1]."""
    C=C[:-1]
    idx=rdp(np.vstack([C,C[:1]]),simplify)[:-1]
    V=C[idx]
    n=len(V); corners=[]
    for k in range(n):
        a=V[k]-V[k-1]; b=V[(k+1)%n]-V[k]
        ang=np.degrees(np.arccos(np.clip(np.dot(unit(a),unit(b)),-1,1)))
        if ang>corner: corners.append(idx[k])
    if not corners: corners=[0]
    segs=[]
    N=len(C)
    for j,c in enumerate(corners):
        e=corners[(j+1)%len(corners)]
        P=np.array([C[(c+k)%N] for k in range(((e-c)%N or N)+1)])
        if len(P)<2: continue
        r=rdp(P,straight)
        if len(r)==2: segs.append(('L',P[-1],P[0]))
        else:
            if len(P)>12 and smooth>1:
                w=np.ones(smooth)/smooth
                Ps=P.copy()
                Ps[:,0]=np.convolve(np.pad(P[:,0],smooth//2,mode='edge'),w,'valid')
                Ps[:,1]=np.convolve(np.pad(P[:,1],smooth//2,mode='edge'),w,'valid')
                Ps[0]=P[0]; Ps[-1]=P[-1]; P=Ps
            k=min(4,len(P)-1)
            t1=unit(P[k]-P[0]); t2=unit(P[-1-k]-P[-1])
            for b in fit_cubic(P,t1,t2,maxerr): segs.append(('C',b,P[0]))
    return segs
def to_d(segs, f=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')):
    if not segs: return ''
    st=segs[0][2]; d=f'M {f(st[0])} {f(st[1])}'
    for s in segs:
        if s[0]=='C':
            b=s[1]; ab=b[3]-b[0]; L=np.hypot(*ab)
            if L>0 and max(abs(ab[0]*(p[1]-b[0][1])-ab[1]*(p[0]-b[0][0]))/L for p in b[1:3])<2.0: s=('L',b[3],s[2])
        if s[0]=='L': d+=f' L {f(s[1][0])} {f(s[1][1])}'
        else:
            b=s[1]; d+=' C '+' '.join(f'{f(p[0])} {f(p[1])}' for p in b[1:])
    return d+' Z'
def mask_to_d(mask, sigma=0.8, **kw):
    m=gaussian_filter(mask.astype(float),sigma)
    m=np.pad(m,2)
    ds=[]
    for c in find_contours(m,0.5):
        if len(c)<8 or (np.ptp(c[:,0])<4 and np.ptp(c[:,1])<4): continue
        C=np.c_[c[:,1]-1.5,c[:,0]-1.5]  # pixel-centre -> pixel-edge coordinates
        ds.append(to_d(fit_contour(C,**kw)))
    return ' '.join(ds)
