#!/usr/bin/env python3
"""Build the Forest Service card from reusable vector components.

SVG generation uses Python's standard library only. Pass --render to export
preview PNGs and vector PDFs with CairoSVG. No photograph is traced or embedded.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)

PAPER = '#E8DDB4'
DARK = '#282C20'
SOURCE_URL = 'https://github.com/ahzs645/PofBC/blob/main/src/internal/forest-service-lands-department.svg'
TITLE = 'British Columbia Forest Service - Prevent Forest Fires card'

def el(tag, **attrs):
    return ET.Element('{'+SVG+'}'+tag, {k.replace('_', '-'): str(v) for k,v in attrs.items()})

def layer(id_, label):
    g=el('g', id=id_)
    g.set('{'+INK+'}groupmode', 'layer')
    g.set('{'+INK+'}label', label)
    return g

def recolour(node, ink, paper):
    for e in node.iter():
        for attr in ['fill','stroke']:
            value=e.get(attr,'').upper()
            if value in ['#000000','#000','BLACK']:
                e.set(attr,ink)
            elif value in ['#FFFFFF','#FFF','WHITE']:
                e.set(attr,paper)
    return node

def prefixed(node, prefix):
    # These components have no external references, masks, or linked assets.
    for e in node.iter():
        if e.get('id'):
            e.set('id',prefix+e.get('id'))
    return node

def make_card(source, output, fit=True, white=False):
    metadata=json.loads((source/'layout.json').read_text())
    paper='#FFFFFF' if white else PAPER
    ink='#000000' if white else DARK
    root=el('svg',version='1.1',width='210mm',height='100mm',viewBox='0 0 1050 500')
    title=el('title'); title.text=TITLE; root.append(title)
    desc=el('desc')
    desc.text=('Editable vector reconstruction from the supplied photograph. '+
        ('Existing logo components are repositioned and scaled to the card layout; the central seal retains its own proportions. ' if fit else
         'The complete supplied PofBC logo is uniformly scaled without changing its internal proportions. ')+
        'Text is outlined reconstructed lettering based on condensed C059 Bold, with adjusted lowercase proportions. '+
        'This is an approximation, not an identified historic typeface. Solid paper is a separate layer. '+
        'The 210 by 100 mm output size is a convenient new print size, not a measured original size. '+
        'No raster images, external resources, or live font dependencies.')
    root.append(desc)
    meta=el('metadata'); meta.text=json.dumps({
        'source_logo':SOURCE_URL,
        'source_sha256':hashlib.sha256((source/'website-logo.svg').read_bytes()).hexdigest(),
        'version':'card-layout-fit' if fit else 'original-logo-proportions',
        'artboard':[1050,500],
        'physical_size_mm':[210,100],
        'text_lines':['“England Expects Every Man to Do His Duty.”','Do Yours: Prevent Forest Fires.'],
        'font_note':'Reconstructed outlines based on horizontally condensed C059 Bold; historical font not confirmed.'
    },ensure_ascii=False)
    root.append(meta)
    background=layer('paper','01 - Paper colour')
    background.append(el('rect',x=0,y=0,width=1050,height=500,fill=paper))
    root.append(background)
    frame=layer('border','02 - Printed border')
    endpoints=metadata['top_arms_fit' if fit else 'top_arms_original']
    frame.append(el('path',id='border-rule',d=f'M {endpoints[0]} 137 H 95 V 450 H 955 V 137 H {endpoints[1]}',
                     fill='none',stroke=ink,stroke_width='3',stroke_linejoin='miter',stroke_linecap='butt'))
    root.append(frame)
    logo=layer('forest-service-logo','03 - Forest Service emblem')
    logo.set('fill',ink)
    if fit:
        comp=ET.parse(source/'fitted-logo.svg').getroot()
        for child in comp:
            if child.tag.rsplit('}',1)[-1] in ['g','path','ellipse','circle','defs']:
                logo.append(prefixed(recolour(copy.deepcopy(child),ink,paper),'logo-'))
    else:
        comp=ET.parse(source/'website-logo.svg').getroot()
        g=el('g',transform=metadata['original_logo_transform'])
        for child in comp:
            if child.tag.rsplit('}',1)[-1] in ['g','path','ellipse','circle','defs']:
                g.append(prefixed(recolour(copy.deepcopy(child),ink,paper),'logo-'))
        logo.append(g)
    root.append(logo)
    text=layer('card-lettering','04 - Outlined card lettering')
    text.set('fill',ink)
    comp=ET.parse(source/'lettering.svg').getroot()
    for child in comp:
        if child.tag.rsplit('}',1)[-1] in ['g','path','defs']:
            text.append(prefixed(recolour(copy.deepcopy(child),ink,paper),'type-'))
    root.append(text)
    ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=True)

def build(source,output,render=False):
    output.mkdir(parents=True,exist_ok=True)
    variants=[
        ('forest-service-card',True,False),
        ('forest-service-card-white',True,True),
        ('forest-service-card-original-logo',False,False),
        ('forest-service-card-original-logo-white',False,True),
    ]
    for name,fit,white in variants:
        svg=output/(name+'.svg')
        make_card(source,svg,fit,white)
        print(svg.name)
    if render:
        import cairosvg
        for name in ['forest-service-card','forest-service-card-original-logo']:
            cairosvg.svg2png(url=str(output/(name+'.svg')),write_to=str(output/(name+'-preview.png')),
                            output_width=3150,output_height=1500)
        for name in ['forest-service-card','forest-service-card-original-logo']:
            cairosvg.svg2pdf(url=str(output/(name+'-white.svg')),write_to=str(output/(name+'.pdf')))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path(__file__).parent)
    p.add_argument('--output',type=Path,default=Path(__file__).parent.parent/'artwork')
    p.add_argument('--render',action='store_true')
    a=p.parse_args(); build(a.source,a.output,a.render)
