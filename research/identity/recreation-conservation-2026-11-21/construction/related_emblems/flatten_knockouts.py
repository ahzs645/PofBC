"""Resolve vector knockout masks with exact curve booleans (skia-pathops).

No raster tracing is involved. The source component paths remain in each
construction SVG; exported production SVGs contain a single compound outline.
"""
import sys,re,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'dependencies'))
import pathops
import numpy as np
from lxml import etree
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen

def op(a,b,kind):
    a.convertConicsToQuads(.002)
    b.convertConicsToQuads(.002)
    return pathops.op(a,b,kind)

def transforms(s):
    result=np.eye(3)
    for name,values in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)',s or ''):
        a=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',values)];m=np.eye(3)
        if name=='matrix':m=np.array([[a[0],a[2],a[4]],[a[1],a[3],a[5]],[0,0,1.]])
        elif name=='translate':m[0,2]=a[0];m[1,2]=a[1] if len(a)>1 else 0
        elif name=='scale':m[0,0]=a[0];m[1,1]=a[1] if len(a)>1 else a[0]
        elif name=='rotate':
            ang=math.radians(a[0]);m[:2,:2]=[[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]]
            if len(a)>2:
                t=np.eye(3);t[:2,2]=a[1:3];ti=np.eye(3);ti[:2,2]=[-a[1],-a[2]];m=t@m@ti
        result=result@m
    return result

def ellipse_d(cx,cy,rx,ry):
    k=.5522847498307936
    return f'M{cx+rx} {cy}C{cx+rx} {cy+ry*k} {cx+rx*k} {cy+ry} {cx} {cy+ry}C{cx-rx*k} {cy+ry} {cx-rx} {cy+ry*k} {cx-rx} {cy}C{cx-rx} {cy-ry*k} {cx-rx*k} {cy-ry} {cx} {cy-ry}C{cx+rx*k} {cy-ry} {cx+rx} {cy-ry*k} {cx+rx} {cy}Z'

def shape(n):
    tag=etree.QName(n).localname;f=lambda k,default=0:float(n.get(k,default));d=''
    if tag=='path':d=n.get('d','')
    elif tag in ['circle','ellipse']:
        rx=f('r') if tag=='circle' else f('rx');ry=f('r') if tag=='circle' else f('ry');d=ellipse_d(f('cx'),f('cy'),rx,ry)
    elif tag=='rect':
        x,y,w,h=f('x'),f('y'),f('width'),f('height');rx=min(f('rx'),w/2);ry=min(f('ry',rx),h/2);k=.5522847498307936
        if not rx:d=f'M{x} {y}h{w}v{h}h{-w}Z'
        else:d=f'M{x+rx} {y}H{x+w-rx}C{x+w-rx+k*rx} {y} {x+w} {y+ry-k*ry} {x+w} {y+ry}V{y+h-ry}C{x+w} {y+h-ry+k*ry} {x+w-rx+k*rx} {y+h} {x+w-rx} {y+h}H{x+rx}C{x+rx-k*rx} {y+h} {x} {y+h-ry+k*ry} {x} {y+h-ry}V{y+ry}C{x} {y+ry-k*ry} {x+rx-k*rx} {y} {x+rx} {y}Z'
    p=pathops.Path()
    if d:parse_path(d,p.getPen())
    return p

def flatten(svg):
    root=etree.fromstring(svg.encode());ids={n.get('id'):n for n in root.iter() if n.get('id')}
    def paint_group(node,parent=np.eye(3),style=None,mask_mode=False):
        style=dict(style or {'fill':'black','stroke':'none','stroke-width':'1'})
        for attr in ['fill','stroke','stroke-width','stroke-linecap','stroke-linejoin']:
            if node.get(attr) is not None:style[attr]=node.get(attr)
        m=parent@transforms(node.get('transform'));tag=etree.QName(node).localname
        geometry=pathops.Path()
        if tag in ['g','svg','mask']:
            for child in node:
                if etree.QName(child).localname in ['defs','title','desc']:continue
                child_geom,child_color=paint_group(child,m,style,mask_mode)
                mode=pathops.PathOp.DIFFERENCE if tag=='mask' and child_color=='black' else pathops.PathOp.UNION
                geometry=op(geometry,child_geom,mode)
            # A group has already applied its internal mask paint sequence.
            color='white' if tag=='mask' else style.get('fill','black')
        else:
            p=shape(node);color=style.get('fill','black')
            if color!='none':geometry=pathops.Path(p)
            if style.get('stroke','none')!='none':
                q=pathops.Path(p);cap=pathops.LineCap.ROUND_CAP if style.get('stroke-linecap')=='round' else pathops.LineCap.BUTT_CAP
                join=pathops.LineJoin.ROUND_JOIN if style.get('stroke-linejoin')=='round' else pathops.LineJoin.MITER_JOIN
                q.stroke(float(style.get('stroke-width',1)),cap,join,4);geometry=op(geometry,q,pathops.PathOp.UNION)
                if color=='none':color=style['stroke']
            geometry=geometry.transform(m[0,0],m[1,0],m[0,1],m[1,1],m[0,2],m[1,2])
        if node.get('mask'):
            mid=re.search(r'#([^)]*)',node.get('mask')).group(1)
            mk,_=paint_group(ids[mid],m,None,True);geometry=op(geometry,mk,pathops.PathOp.INTERSECTION)
        return geometry,color
    geom,_=paint_group(root);geom.convertConicsToQuads(.005);pen=SVGPathPen(None);geom.draw(pen)
    out=etree.Element('{http://www.w3.org/2000/svg}svg',nsmap={None:'http://www.w3.org/2000/svg'})
    for k in ['viewBox','width','height']:out.set(k,root.get(k))
    for n in root:
        if etree.QName(n).localname in ['title','desc']:out.append(n)
    path=etree.SubElement(out,'{http://www.w3.org/2000/svg}path');path.set('d',pen.getCommands());path.set('fill','#000000');path.set('fill-rule','nonzero')
    return etree.tostring(out,encoding='unicode')
