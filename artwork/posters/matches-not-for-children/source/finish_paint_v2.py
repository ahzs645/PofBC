#!/usr/bin/env python3
"""Finalize the reconstructed paint, preserving eight editable path layers.

The large field geometry is manually authored. Texture comes from the supplied
study's seeded paint-deposition model. No original photograph contours enter the
construction. The RGB offset below is a robust photo-appearance match estimated
from explicit background-only regions; it is not physical ink calibration.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,copy

ROOT=Path(__file__).resolve().parent
BUILD=ROOT/'paint-rebuild'
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVG);ET.register_namespace('inkscape',INK)
RGB_OFFSET=(-7,-21,-10)
MATRIX='matrix(1.510574018 0 0 1.508620690 -9.063444109 -12.068965517)'

def photo_colour(c):
    if not c or not c.startswith('#') or len(c)!=7:return c
    vals=[int(c[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{max(0,min(255,v+d)):02x}' for v,d in zip(vals,RGB_OFFSET))

def newroot(title):
    r=ET.Element('{'+SVG+'}svg',{'width':'1000','height':'1400','viewBox':'0 0 1000 1400','version':'1.1'})
    ET.SubElement(r,'{'+SVG+'}title').text=title
    ET.SubElement(r,'{'+SVG+'}desc').text=('Editable all-path paint reconstruction. Source study native painted area x=6..668, y=8..936 is mapped to the 1000 by 1400 comparison plane. Large paint fields are manually composed; grain is synthesized from the supplied study model. RGB palette is adjusted to the supplied photograph, without claiming original-ink or print calibration. No raster image, live filter, gradient, external reference or opacity effect.')
    return r

def prepare(g):
    g=copy.deepcopy(g);g.set('transform',MATRIX)
    for e in g.iter():
        if e.get('fill'):e.set('fill',photo_colour(e.get('fill')))
        if e.get('stroke') and e.get('stroke')!='none':e.set('stroke',photo_colour(e.get('stroke')))
        if e.get('id'):e.set('id','paint-v2-'+e.get('id'))
    return g

src=ET.parse(BUILD/'output'/'paint-background.svg').getroot()
root=newroot('BC Forest Service poster - revised paint reconstruction')
for g in src:
    if g.tag.rsplit('}',1)[-1]=='g':root.append(prepare(g))
# The original lower print edge is continuous red. Extend its undercoat beyond
# the crop before adding the textured colour passes, so ragged generated ends
# cannot expose the yellow ground as an artificial sawtooth border.
under=next(g for g in root if g.get('id')=='paint-v2-underpainting')
under.insert(0,ET.Element('{'+SVG+'}path',{'id':'paint-v2-lower-red-undercoat-extension','fill':photo_colour('#E53518'),'d':'M0,892 H685 V950 H0 Z'}))
# Avoid exposing pale study-paper at the cleaned rectangular crop edge.
first=next(g for g in root if g.tag.rsplit('}',1)[-1]=='g')
firstpath=next(p for p in first.iter() if p.tag.rsplit('}',1)[-1]=='path')
firstpath.set('fill',photo_colour('#F9D617'))
last=next(g for g in reversed(list(root)) if g.tag.rsplit('}',1)[-1]=='g')
ET.SubElement(last,'{'+SVG+'}path',{'id':'paint-v2-lower-print-edge','fill':photo_colour('#E53518'),'d':'M6,933.5 H668 V937 H6 Z'})
ET.ElementTree(root).write(ROOT/'paint_v2.svg',encoding='utf-8',xml_declaration=True)

construction=ET.parse(BUILD/'work'/'construction-geometries.svg').getroot()
clean=newroot('BC Forest Service poster - simplified revised paint construction')
keep={'paper','yellow-ground','underpainting','orange-masses','paint-overlaps'}
for g in construction:
    if g.get('id') in keep:
        cp=prepare(g)
        if g.get('id')=='paper':
            for p in cp.iter():
                if p.get('fill'):p.set('fill',photo_colour('#F9D617'))
        clean.append(cp)
ET.ElementTree(clean).write(ROOT/'paint_v2_clean.svg',encoding='utf-8',xml_declaration=True)

stats={}
for file in ['paint_v2.svg','paint_v2_clean.svg']:
    p=ROOT/file;t=ET.parse(p).getroot();counts={}
    for e in t.iter():
        name=e.tag.rsplit('}',1)[-1];counts[name]=counts.get(name,0)+1
    stats[file]={'bytes':p.stat().st_size,'path_objects':counts.get('path',0),'compound_subpaths':sum(e.get('d','').count('M') for e in t.iter()),'named_layers':sum(e.tag.rsplit('}',1)[-1]=='g' for e in t),'images':counts.get('image',0),'filters':counts.get('filter',0),'live_text':counts.get('text',0),'opacity_attributes':sum('opacity' in e.attrib for e in t.iter()),'external_hrefs':sum(any(k.rsplit('}',1)[-1]=='href' for k in e.attrib) for e in t.iter())}
(ROOT/'paint_v2_validation.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
