#!/usr/bin/env python3
"""Convert a synthesized paint-deposition model into opaque editable SVG paths.

Inputs are the manually composed polygon study from build_paint_study.py, never
the reference screenshot. The final SVG contains no image data or SVG filters.
"""
from pathlib import Path
import math, re, json, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, distance_transform_edt
import contourpy
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'; WORK=ROOT/'work'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=WORK/'construction-geometries.svg'
if not SOURCE.exists(): shutil.copyfile(OUT/'paint-background.svg',SOURCE)
source=ET.parse(SOURCE).getroot()
W,H=685,937
S=1.5
NX,NY=round(W*S),round(H*S)
SH=(NY,NX)
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVG); ET.register_namespace('inkscape',INK)
rng=np.random.default_rng(672311)

def field(sy,sx):
    a=gaussian_filter(rng.standard_normal(SH).astype('float32'),(sy*S,sx*S))
    return a/(a.std()+1e-5)

coarse=field(13,7)
medium=field(3.8,1.7)
fine=field(.55,.35)
fibres=field(6,.65)
scrapes=field(.6,4.4)
broad=field(28,17)
grain=.5*medium+.42*fine+.3*scrapes
shift=3.0*coarse+1.6*medium+.55*fine
clip=np.zeros(SH,bool)
clip[round(8*S):round(936*S),round(6*S):round(668*S)]=True
stats={'layers':{},'subpaths':0,'nodes':0}

def newroot():
    root=ET.Element('{'+SVG+'}svg',{'width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}','version':'1.1'})
    ET.SubElement(root,'title').text='Painted background — all-path reconstruction study'
    ET.SubElement(root,'desc').text=(
        'Art-directed reconstruction study of the supplied poster background. '
        'Major colour placement was mapped manually, then textured with a seeded, '
        'multiscale paint-deposition model and saved as opaque filled SVG paths. '
        'No source-image tracing, embedded raster, SVG filters, gradients, or opacity effects. '
        'Unseen paint behind lettering and illustration is inferred. Colours are approximate. '
        'This is an editable interpretation, not a facsimile of the historic printed surface.')
    return root

root=newroot()

def group(id,label,parent=root):
    return ET.SubElement(parent,'g',{'id':id,'{'+INK+'}groupmode':'layer','{'+INK+'}label':label})

def polygon_mask(element):
    im=Image.new('1',(NX,NY),0); draw=ImageDraw.Draw(im)
    if element.tag.split('}')[-1]=='path': els=[element]
    else: els=list(element.iter())
    for e in els:
        if e.tag.split('}')[-1]!='path': continue
        d=e.get('d','')
        # Construction source consists only of closed M/L polygons.
        if re.search('[CAQSTHVcaqsthv]',d): continue
        vals=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',d)))
        pts=[(round(vals[i]*S),round(vals[i+1]*S)) for i in range(0,len(vals),2)]
        if len(pts)>2: draw.polygon(pts,fill=1)
    return np.array(im,dtype=bool)

def deposit(mask,kind):
    di=distance_transform_edt(mask)/S
    do=distance_transform_edt(~mask)/S
    signed=di-do
    if kind=='orange':
        arr=(signed+shift*1.1>0)
        arr &= ~(grain+.26*coarse>2.05)
    elif kind=='under':
        arr=(signed+shift*1.9>1.0)
        arr &= (grain+.48*coarse > -.9)
    else:
        arr=(signed+shift*1.3>0)
        arr &= (grain+.28*coarse> -1.3)
    return arr & clip, di

def area(v):
    return abs(float(np.sum(v[:-1,0]*v[1:,1]-v[1:,0]*v[:-1,1])))/2

def rdp(v,tol=.18):
    if len(v)<5:return v
    # Use a fast running line-deviation reduction. Preserve irregular corners.
    keep=[0]; last=0
    for k in range(2,len(v)):
        dv=v[k]-v[last]
        length=math.hypot(*dv)
        if length==0: continue
        middle=v[last+1:k]-v[last]
        dist=np.abs(middle[:,0]*dv[1]-middle[:,1]*dv[0])/length
        if len(dist) and dist.max()>tol:
            keep.append(k-1);last=k-1
    if keep[-1]!=len(v)-1: keep.append(len(v)-1)
    return v[keep]

def paths(parent,mask,col,id,min_area=.13,smooth=.48):
    # Contour the synthesized coverage; no pixels from the supplied photo enter.
    z=gaussian_filter(mask.astype('float32'),smooth)
    z=np.pad(z,1)
    gen=contourpy.contour_generator(z=z,fill_type='OuterOffset',corner_mask=True)
    polys,offsets=gen.filled(.5,1.5)
    commands=[]; polygons=0; nodes=0
    for pp,oo in zip(polys,offsets):
        outer=(pp[oo[0]:oo[1]]-1)/S
        if area(outer)<min_area: continue
        for a,b in zip(oo[:-1],oo[1:]):
            v=(pp[a:b]-1)/S
            if area(v)<min_area:continue
            v=rdp(v,.13)
            if len(v)<4:continue
            commands.append('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in v[:-1])+'Z')
            polygons+=1;nodes+=len(v)-1
    if commands:
        ET.SubElement(parent,'path',{'id':id,'fill':col,'fill-rule':'evenodd','d':' '.join(commands)})
    stats['subpaths']+=polygons;stats['nodes']+=nodes
    return polygons

def adjust(hexcol,delta):
    c=[int(hexcol[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{max(0,min(255,k+d)):02X}' for k,d in zip(c,delta))

def surfacepaths(parent,mask,col,id,min_area=.13,smooth=.48):
    """Keep pale scumbling thin over the manually composed opaque orange cores.

    This is an art-directed material adjustment using synthetic construction
    masks only. It prevents bright yellow gaps from erasing the major shapes.
    """
    c=[int(col[i:i+2],16) for i in (1,3,5)]
    if c[1] / max(c[0],1) < .65:
        return paths(parent,mask,col,id,min_area,smooth)
    covered=mask&all_orange
    outside=mask&~all_orange
    warm=[244,82,12]
    thin='#'+''.join(f'{round(.25*a+.75*b):02X}' for a,b in zip(c,warm))
    return (paths(parent,outside,col,id+'-yellow',min_area,smooth)+
            paths(parent,covered,thin,id+'-thin-over-orange',min_area,smooth))

base=group('paper-and-yellow','01 · Paper and yellow ground')
ET.SubElement(base,'path',{'fill':'#E8F0E6','d':'M0,0H685V937H0Z'})
paths(base,clip,'#F9D617','yellow-ground',min_area=1,smooth=.2)

# Fine low-contrast variation in the yellow ground, concentrated into patches.
yg=group('yellow-pigment','02 · Yellow pigment variations')
for idx,(threshold,col) in enumerate([(-.3,'#FAD918'),(.35,'#FBDC1A'),(1.10,'#FBDD20')]):
    tone=(.43*coarse+.34*medium+.12*scrapes+.16*broad>threshold)&clip
    paths(yg,tone,col,f'yellow-pigment-{idx}',min_area=.3)

source_groups={e.get('id'):e for e in source if e.tag.split('}')[-1]=='g'}
all_orange=np.zeros(SH,bool)
for srcid,title,kind in [
    ('underpainting','03 · Broken amber underpainting','under'),
    ('orange-masses','04 · Orange paint pulls','orange'),
    ('paint-overlaps','05 · Yellow overpainting and scraped areas','over')
]:
    g=group(srcid,title)
    num=0
    for i,e in enumerate(source_groups[srcid]):
        if e.tag.split('}')[-1]!='path': continue
        original=polygon_mask(e)
        mask,di=deposit(original,kind)
        col=e.get('fill')
        # Yellow tonal underpainting should not look like flat ochre islands.
        if srcid=='underpainting' and col=='#F7CA12': col='#F6D11A'
        if srcid=='underpainting' and col=='#FAB00B': col='#F8B911'
        if kind=='orange':all_orange |= mask
        p=ET.SubElement(g,'g',{'id':f'{srcid}-pass-{i+1}'})
        draw=surfacepaths if srcid=='paint-overlaps' else paths
        num+=draw(p,mask,col,f'{srcid}-body-{i+1}',min_area=.17)
        if kind=='orange':
            tex=.32*coarse+.37*medium+.26*scrapes+.13*fine
            # Continuous pigment deposits retain opaque cores with irregular detail.
            for j,(thr,delta) in enumerate([(-.10,(1,5,-1)),(.52,(3,11,-1)),(1.18,(5,18,0))]):
                tm=mask&(tex>thr)
                num+=paths(p,tm,adjust(col,delta),f'{srcid}-pigment-{i+1}-{j}',min_area=.18)
            edge=mask&(di<11)&(grain>.55)
            num+=paths(p,edge,adjust(col,(3,23,0)),f'{srcid}-edge-pigment-{i+1}',min_area=.25)
        else:
            tex=(.38*coarse+.52*medium+.18*scrapes)
            tm=mask&(tex>.55)
            num+=draw(p,tm,adjust(col,(1,5,1)),f'{srcid}-pigment-{i+1}',min_area=.23)
    stats['layers'][srcid]=num

# Preserve selected art-directed scuffs, but break their regular geometry.
g=group('brush-residue','06 · Fragmented brush residue')
colormasks={}
for srcid in ['directional-scuffs','paint-fragments']:
    sg=source_groups[srcid]
    for e in sg.iter():
        if e.tag.split('}')[-1]!='path':continue
        col=e.get('fill')
        mm=polygon_mask(e)
        if col in colormasks:colormasks[col]|=mm
        else:colormasks[col]=mm
for i,(col,mm) in enumerate(colormasks.items()):
    # Remove regular one-dimensional hatch patterns by breaking them with grain.
    mm &= ((medium*.35+fine*.55+scrapes*.30)>-.23)
    surfacepaths(g,mm&clip,col,f'brush-residue-{i}',min_area=.24)

# Additional broad horizontal scumble patches, each with layered irregular gaps.
g=group('scraped-paint','07 · Directional scumbling')
yy,xx=np.mgrid[:NY,:NX]
for i,(x,y,w,h,col,cov) in enumerate([
    (10,161,119,35,'#F45B0C',.0),(16,329,107,31,'#F9D318',.2),
    (6,447,64,52,'#F8D318',.2),(26,556,62,38,'#F7CC13',.5),
    (63,603,128,73,'#F6C313',.3),(129,620,232,93,'#F2660C',.45),
    (295,297,52,123,'#F8C815',.55),(332,420,63,49,'#FAD518',.4),
    (379,466,35,97,'#FAD31B',.5),(369,590,46,67,'#F9D318',.5),
    (468,305,40,233,'#F8B10C',.7),(607,497,48,183,'#F9CC18',.6),
    (484,818,121,43,'#FAD91C',.2)
]):
    edge=np.minimum.reduce([(xx/S-x)/max(3,w*.1),(x+w-xx/S)/max(3,w*.1),
                           (yy/S-y)/max(3,h*.12),(y+h-yy/S)/max(3,h*.12)])
    texture=.45*medium+.45*scrapes+.20*fine+.35*coarse
    shape=(edge+coarse*.4>0)&(texture>cov)&clip
    surfacepaths(g,shape,col,f'scumble-{i}',min_area=.23)

# Fine directional highlights, sparse and with colour tied to the underlying paint.
g=group('fine-paint-skips','08 · Small paint skips')
texture=.5*fibres+.4*fine+.4*medium
for i,(mask,col) in enumerate([
    (all_orange&(texture>1.8),'#F9870C'),
    ((~all_orange)&clip&(texture>2.0)&(coarse>.25),'#F2BE11')
]): paths(g,mask,col,f'fine-skips-{i}',min_area=.16)

def save(name,reserve=False):
    clone=ET.fromstring(ET.tostring(root))
    if reserve:
        rr=ET.parse(WORK/'reserve-layer.svg').getroot()
        for e in rr.iter():
            if e.get('id')=='illustration-reserve':
                g=ET.fromstring(ET.tostring(e));g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label','09 · Optional pale illustration reserve')
                clone.append(g);break
    target=OUT/name
    ET.ElementTree(clone).write(target,encoding='utf-8',xml_declaration=True)
    stats[name]={'bytes':target.stat().st_size,'paths':sum(e.tag.split('}')[-1]=='path' for e in clone.iter()),
                 'images':sum(e.tag.split('}')[-1]=='image' for e in clone.iter()),
                 'filters':sum(e.tag.split('}')[-1]=='filter' for e in clone.iter())}

save('paint-background.svg')
(WORK/'refined-validation.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
