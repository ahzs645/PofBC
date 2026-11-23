#!/usr/bin/env python3
"""Generate regular five-point stars from the saved landmark measurements.

Usage: python3 source/generate_stars.py Newspaper /tmp/newspaper-stars.svg
       python3 source/generate_stars.py CIPO /tmp/cipo-stars.svg

This generator uses no images or image-processing dependencies. The output is a
standalone SVG component. The packaged component files retain their additional
editing groups and descriptive IDs.
"""
from pathlib import Path
import argparse,json,math,xml.etree.ElementTree as ET
SVG='http://www.w3.org/2000/svg';ET.register_namespace('',SVG)
def tag(t):return '{'+SVG+'}'+t
def generate(layout,output):
    source=Path(__file__).resolve().parent/'construction'/('stars-newspaper.json' if layout=='Newspaper' else 'stars-cipo.json')
    data=json.loads(source.read_text());vb=data['viewBox'];ratio=data.get('innerRatio',data.get('inner_ratio'))
    root=ET.Element(tag('svg'),{'viewBox':' '.join(map(str,vb)),'width':str(vb[2]),'height':str(vb[3])})
    ET.SubElement(root,tag('title')).text=f'SuperHost {layout} star geometry'
    group=ET.SubElement(root,tag('g'),{'id':'star-spray','fill':'#000000'})
    unit=[]
    for k in range(10):
        a=-math.pi/2+k*math.pi/5;r=1 if k%2==0 else ratio
        unit.append((r*math.cos(a),r*math.sin(a)))
    path='M'+' L'.join(f'{x:.7f} {y:.7f}' for x,y in unit)+' Z'
    for i,star in enumerate(data['stars']):
        rx=star.get('rx',star.get('r'));ry=star.get('ry',star.get('r'))
        ET.SubElement(group,tag('path'),{'id':f'star-{i:03}',
            'd':path,'transform':f'translate({star["x"]:.7f} {star["y"]:.7f}) scale({rx:.7f} {ry:.7f}) rotate({star["rotation"]+90:.7f})',
            'data-position-source':star['source']})
    ET.indent(root,space='  ');ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=True)
    print(f'Wrote {len(data["stars"])} analytic stars to {output}')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('layout',choices=['Newspaper','CIPO']);p.add_argument('output',type=Path);a=p.parse_args();generate(a.layout,a.output)
