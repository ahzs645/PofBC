"""Reconstruct source penwork as fitted, variable-width vector strokes.

This is a source-guided reconstruction, not the invented procedural hatching
of v1. Hand-authored anatomical masks isolate and organise the animal. The
medial stroke network and its measured widths preserve the illustrator's pen
decisions; short Bezier envelopes remove raster stair-steps. No pixels are
embedded in the delivered SVG.
"""
from pathlib import Path
from collections import defaultdict
from math import hypot, sqrt
import json, math, re, subprocess, tempfile
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
TMP=ROOT/'_work'
SOURCE=ROOT/'reference'
TMP.mkdir(exist_ok=True,parents=True)
INK='#326c59'
NS='http://www.w3.org/2000/svg'

def thin(binary):
    """Topology-preserving two-subpass thinning of the measured ink plate."""
    a=np.pad(binary.astype(np.uint8),1)
    for iteration in range(150):
        changed=False
        for sub in (0,1):
            p=a[1:-1,1:-1]
            n=[a[:-2,1:-1],a[:-2,2:],a[1:-1,2:],a[2:,2:],a[2:,1:-1],a[2:,:-2],a[1:-1,:-2],a[:-2,:-2]]
            B=sum(n)
            A=sum((n[i]==0)&(n[(i+1)%8]==1) for i in range(8))
            if sub==0:
                c=(n[0]*n[2]*n[4]==0)&(n[2]*n[4]*n[6]==0)
            else:
                c=(n[0]*n[2]*n[6]==0)&(n[0]*n[4]*n[6]==0)
            remove=(p==1)&(B>=2)&(B<=6)&(A==1)&c
            if np.any(remove):
                p[remove]=0;changed=True
        if not changed:break
    return a[1:-1,1:-1].astype(bool)

def paths_from_skeleton(sk):
    h,w=sk.shape
    points=set(np.flatnonzero(sk).tolist())
    neigh={}
    for p in points:
        y,x=divmod(p,w);n=[]
        for dy,dx in [(-1,0),(0,1),(1,0),(0,-1),(-1,1),(1,1),(1,-1),(-1,-1)]:
            yy,xx=y+dy,x+dx
            if not(0<=yy<h and 0<=xx<w):continue
            q=yy*w+xx
            if q not in points:continue
            # Avoid redundant diagonal chords around a one-pixel right angle.
            if dy and dx and (y*w+xx in points or yy*w+x in points):continue
            n.append(q)
        neigh[p]=n
    done=set();result=[]
    def edge(a,b):return(min(a,b),max(a,b))
    def walk(start,nxt):
        ps=[start];a=start;b=nxt;done.add(edge(a,b))
        for _ in range(len(points)+1):
            ps.append(b)
            if len(neigh[b])!=2:break
            nxt=neigh[b][0] if neigh[b][1]==a else neigh[b][1]
            if edge(b,nxt) in done:break
            done.add(edge(b,nxt));a,b=b,nxt
            if b==start:ps.append(b);break
        return np.array([(p%w+.5,p//w+.5) for p in ps],float)
    for p,nn in neigh.items():
        if not nn:result.append(np.array([[p%w+.5,p//w+.5]],float))
        elif len(nn)!=2:
            for q in nn:
                if edge(p,q) not in done:result.append(walk(p,q))
    for p,nn in neigh.items():
        for q in nn:
            if edge(p,q) not in done:result.append(walk(p,q))
    return result

def unit(v):
    n=np.linalg.norm(v)
    return v/max(n,1e-12)

def fit_beziers(points,error=.6):
    """Least-squares cubic fitting with recursive splitting at worst residual."""
    pts=np.asarray(points,dtype=float)
    if len(pts)<2:return []
    # Remove sequential duplicate samples.
    pts=pts[np.r_[True,np.linalg.norm(np.diff(pts,axis=0),axis=1)>1e-8]]
    if len(pts)<2:return []
    def fit(p,t0,t1,depth=0):
        if len(p)==2:
            d=np.linalg.norm(p[1]-p[0])/3
            return [(p[0],p[0]+t0*d,p[-1]+t1*d,p[-1])]
        distances=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
        u=distances/max(distances[-1],1e-8);v=1-u
        b0=v**3;b1=3*u*v*v;b2=3*u*u*v;b3=u**3
        A0=b1[:,None]*t0;A1=b2[:,None]*t1
        rhs=p-((b0+b1)[:,None]*p[0]+(b2+b3)[:,None]*p[-1])
        C=np.array([[np.sum(A0*A0),np.sum(A0*A1)],[np.sum(A0*A1),np.sum(A1*A1)]])
        X=np.array([np.sum(A0*rhs),np.sum(A1*rhs)])
        try:alpha=np.linalg.solve(C,X)
        except np.linalg.LinAlgError:alpha=np.zeros(2)
        length=distances[-1]
        if min(alpha)<length*1e-4 or max(alpha)>length*2:alpha[:]=np.linalg.norm(p[-1]-p[0])/3
        curve=(p[0],p[0]+t0*alpha[0],p[-1]+t1*alpha[1],p[-1])
        fitted=sum(b[:,None]*q for b,q in zip([b0,b1,b2,b3],curve))
        ds=np.linalg.norm(fitted-p,axis=1);split=int(np.argmax(ds))
        if ds[split]<=error or depth>16:return [curve]
        split=max(1,min(len(p)-2,split))
        tangent=unit(p[split-1]-p[split+1])
        if np.linalg.norm(tangent)<.1:tangent=unit(p[split-1]-p[split])
        return fit(p[:split+1],t0,tangent,depth+1)+fit(p[split:],-tangent,t1,depth+1)
    return fit(pts,unit(pts[1]-pts[0]),unit(pts[-2]-pts[-1]))

def n(v):return f'{v:.3f}'
def pt(p):return f'{n(p[0])} {n(p[1])}'
def curve_commands(curves):return ' '.join('C'+pt(a)+' '+pt(b)+' '+pt(c) for _,a,b,c in curves)

def stroke_envelope(points,widths,scale_x,scale_y):
    """Rebuild a pen stroke from its medial curve and local pressure width."""
    p=np.array(points,float);r=np.array(widths,float)
    if len(p)==1:
        x,y=p[0];rr=max(.5,r[0])
        return f'M{n((x-rr)*scale_x)} {n(y*scale_y)} a{n(rr*scale_x)} {n(rr*scale_y)} 0 1 0 {n(2*rr*scale_x)} 0 a{n(rr*scale_x)} {n(rr*scale_y)} 0 1 0 {n(-2*rr*scale_x)} 0Z'
    # Slight geometric smoothing suppresses pixel quantisation, not anatomical detail.
    if len(p)>=5:
        p[1:-1]=.18*p[:-2]+.64*p[1:-1]+.18*p[2:]
        r[1:-1]=.15*r[:-2]+.7*r[1:-1]+.15*r[2:]
    tangent=np.gradient(p,axis=0);L=np.linalg.norm(tangent,axis=1)
    tangent/=np.maximum(L[:,None],.001)
    normal=np.column_stack((-tangent[:,1],tangent[:,0]))
    left=p+normal*r[:,None];right=p-normal*r[:,None]
    left*=np.array([scale_x,scale_y]);right*=np.array([scale_x,scale_y])
    a=fit_beziers(left,.65*scale_x);b=fit_beziers(right[::-1],.65*scale_x)
    pe=p[-1]*[scale_x,scale_y];ps=p[0]*[scale_x,scale_y]
    # Quadratic caps keep the small original strokes soft instead of square.
    cap_e=(p[-1]+tangent[-1]*r[-1]*1.25)*[scale_x,scale_y]
    cap_s=(p[0]-tangent[0]*r[0]*1.25)*[scale_x,scale_y]
    return 'M'+pt(left[0])+' '+curve_commands(a)+' Q'+pt(cap_e)+' '+pt(right[-1])+' '+curve_commands(b)+' Q'+pt(cap_s)+' '+pt(left[0])+'Z'

def measure_ink(rgb):
    rgb=np.asarray(rgb,dtype=float)
    dark=np.array([205.,147.,166.])
    density=np.sum((255-rgb)*dark,axis=2)/np.sum(dark*dark)
    density=ndi.gaussian_filter(density,.38)
    ink=density>.43
    labels,count=ndi.label(ink)
    sizes=np.bincount(labels.ravel());keep=sizes>=4;keep[0]=False
    return keep[labels],density

def render_mask(path,width,height,pw,ph,out):
    svg=f'<svg xmlns="{NS}" viewBox="0 0 {width} {height}"><path d="{path}" fill="white"/></svg>'
    s=out.with_suffix('.svg');s.write_text(svg)
    subprocess.run(['inkscape',str(s),'--export-type=png','--export-filename='+str(out),'--export-width='+str(pw),'--export-height='+str(ph)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return np.asarray(Image.open(out).convert('RGBA'))[:,:,3]>127

def specimen_test(key='bear',width_offset=-.32):
    """Early visual gate before applying the hand-authored anatomical isolation."""
    im=Image.open(SOURCE/(key+'-source.png')).convert('RGB')
    ink,d=measure_ink(im)
    dist=ndi.distance_transform_edt(ink)
    sk=thin(ink);chains=paths_from_skeleton(sk)
    body=[]
    for chain in chains:
        ix=np.clip(chain[:,0].astype(int),0,im.width-1);iy=np.clip(chain[:,1].astype(int),0,im.height-1)
        radii=np.maximum(.48,dist[iy,ix]+width_offset)
        body.append('<path d="'+stroke_envelope(chain,radii,1,1)+'"/>')
    svg=f'<svg xmlns="{NS}" width="{im.width}" height="{im.height}" viewBox="0 0 {im.width} {im.height}"><g fill="{INK}">'+''.join(body)+'</g></svg>'
    (TMP/(key+'-stroke-study.svg')).write_text(svg)
    print(key,'ink pixels',int(ink.sum()),'skeleton',int(sk.sum()),'strokes',len(chains),flush=True)

if __name__=='__main__':
    import sys
    specimen_test(sys.argv[1] if len(sys.argv)>1 else 'bear',float(sys.argv[2]) if len(sys.argv)>2 else -.32)
