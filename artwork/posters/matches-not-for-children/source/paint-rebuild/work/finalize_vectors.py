#!/usr/bin/env python3
"""Simplify redundant nodes and write compact relative paths for the study."""
from pathlib import Path
import re,json,math
import numpy as np
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output';WORK=ROOT/'work'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('','http://www.w3.org/2000/svg');ET.register_namespace('inkscape',INK)

def rdp(points,eps):
    if len(points)<4:return points
    # Simplify two halves so a closed ring never has a zero-length baseline.
    k=int(np.argmax(np.sum((points-points[0])**2,axis=1)))
    if k==0:return points
    def open_part(p):
        keep=np.zeros(len(p),bool);keep[0]=keep[-1]=True;stack=[(0,len(p)-1)]
        while stack:
            a,b=stack.pop()
            if b-a<2:continue
            ab=p[b]-p[a];norm=np.linalg.norm(ab)
            if norm<1e-9:dist=np.linalg.norm(p[a+1:b]-p[a],axis=1)
            else:
                v=p[a+1:b]-p[a]
                dist=np.abs(v[:,0]*ab[1]-v[:,1]*ab[0])/norm
            idx=int(np.argmax(dist))
            if dist[idx]>eps:
                j=a+1+idx;keep[j]=True;stack.extend([(a,j),(j,b)])
        return p[keep]
    a=open_part(points[:k+1]);b=open_part(np.vstack([points[k:],points[:1]]))
    return np.vstack([a[:-1],b[:-1]])

def num(v):
    s=f'{v:.1f}'.rstrip('0').rstrip('.')
    if s=='-0':s='0'
    return s

def optimize_d(d):
    if re.search('[CAQSTHVcaqsthv]',d):return d
    result=[]
    for ring in re.findall(r'M([^M]+)',d):
        v=np.array(list(map(float,re.findall(r'-?\d+(?:\.\d+)?',ring)))).reshape(-1,2)
        if len(v)<3:continue
        ar=abs(np.sum(v[:,0]*np.roll(v[:,1],-1)-np.roll(v[:,0],-1)*v[:,1]))/2
        if ar<.3:continue
        q=rdp(v,.27)
        if len(q)<3:q=v
        q=np.round(q,1)
        delta=np.diff(q,axis=0)
        result.append('M'+num(q[0,0])+','+num(q[0,1])+'l'+' '.join(num(x)+','+num(y) for x,y in delta)+'z')
    return ' '.join(result)

root=ET.parse(OUT/'paint-background.svg').getroot()
for p in root.iter():
    if p.tag.split('}')[-1]=='path':p.set('d',optimize_d(p.get('d','')))
ET.ElementTree(root).write(OUT/'paint-background.svg',encoding='utf-8',xml_declaration=True)

stats={}
for name in ['paint-background.svg']:
    p=OUT/name;t=ET.parse(p).getroot()
    counts={tag:sum(x.tag.split('}')[-1]==tag for x in t.iter()) for tag in ['path','image','filter','text']}
    counts['bytes']=p.stat().st_size
    counts['compound_subpaths']=sum(x.get('d','').count('M') for x in t.iter())
    counts['top_level_layers']=sum(x.tag.split('}')[-1]=='g' for x in t)
    counts['external_references']=sum(any(k.split('}')[-1]=='href' for k in x.attrib) for x in t.iter())
    stats[name]=counts
(WORK/'final-validation.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
