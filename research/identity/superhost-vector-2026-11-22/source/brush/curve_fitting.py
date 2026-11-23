"""Fit cubic Beziers to mathematical nib-offset samples, never to raster contours.

The input paths are generated from hand-authored pen skeletons. This reduces the
many short straight segments from the offset calculation to editable curves.
"""
from pathlib import Path
import math,re,xml.etree.ElementTree as ET

def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def mul(a,s):return (a[0]*s,a[1]*s)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def length(a):return math.hypot(*a)
def unit(a):
    n=length(a)
    return mul(a,1/n) if n else (1,0)
def bez(b,t):
    s=1-t
    return tuple(s*s*s*b[0][k]+3*s*s*t*b[1][k]+3*s*t*t*b[2][k]+t*t*t*b[3][k] for k in (0,1))
def parameterize(p):
    u=[0.]
    for a,b in zip(p,p[1:]):u.append(u[-1]+length(sub(a,b)))
    return [v/u[-1] for v in u]
def generate(p,u,left,right):
    a00=a01=a11=x0=x1=0.
    first,last=p[0],p[-1]
    for q,t in zip(p,u):
        s=1-t;b0=s*s*s;b1=3*s*s*t;b2=3*s*t*t;b3=t*t*t
        a0=mul(left,b1);a1=mul(right,b2)
        v=sub(q,add(mul(first,b0+b1),mul(last,b2+b3)))
        a00+=dot(a0,a0);a01+=dot(a0,a1);a11+=dot(a1,a1)
        x0+=dot(a0,v);x1+=dot(a1,v)
    det=a00*a11-a01*a01
    a=(x0*a11-x1*a01)/det if abs(det)>1e-15 else 0
    b=(a00*x1-a01*x0)/det if abs(det)>1e-15 else 0
    chord=length(sub(first,last))
    if a<1e-6*chord or b<1e-6*chord:a=b=chord/3
    return [first,add(first,mul(left,a)),add(last,mul(right,b)),last]
def maximum(p,b,u):
    err=-1;split=len(p)//2
    for i in range(1,len(p)-1):
        d=sub(bez(b,u[i]),p[i]);e=dot(d,d)
        if e>err:err=e;split=i
    return err,split
def newton(b,p,t):
    q=bez(b,t);s=1-t
    d=[mul(sub(b[i+1],b[i]),3) for i in range(3)]
    dd=[mul(sub(d[i+1],d[i]),2) for i in range(2)]
    v=add(add(mul(d[0],s*s),mul(d[1],2*s*t)),mul(d[2],t*t))
    vv=add(mul(dd[0],s),mul(dd[1],t))
    diff=sub(q,p);den=dot(v,v)+dot(diff,vv)
    return max(0,min(1,t-dot(diff,v)/den)) if abs(den)>1e-14 else t
def fit(p,left,right,error):
    if len(p)==2:
        d=length(sub(p[1],p[0]))/3
        return [[p[0],add(p[0],mul(left,d)),add(p[1],mul(right,d)),p[1]]]
    u=parameterize(p);b=generate(p,u,left,right);err,split=maximum(p,b,u)
    if err<=error*error:return [b]
    if err<error*error*9:
        for _ in range(5):
            u2=[newton(b,q,t) for q,t in zip(p,u)]
            if any(x>y for x,y in zip(u2,u2[1:])):break
            b=generate(p,u2,left,right);err,split=maximum(p,b,u2)
            if err<=error*error:return [b]
            u=u2
    middle=unit(sub(p[split-1],p[split+1]))
    return fit(p[:split+1],left,middle,error)+fit(p[split:],mul(middle,-1),right,error)

def simplify(d,error=.09):
    values=[float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',d)]
    points=list(zip(values[0::2],values[1::2]))
    points=[q for i,q in enumerate(points) if i==0 or q!=points[i-1]]
    points.append(points[0])
    curves=fit(points,unit(sub(points[1],points[0])),unit(sub(points[-2],points[-1])),error)
    f=lambda q:f'{q[0]:.3f} {q[1]:.3f}'
    return 'M'+f(points[0])+''.join(' C'+' '.join(f(q) for q in b[1:]) for b in curves)+' Z',len(points),len(curves)

