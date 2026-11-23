#!/usr/bin/env python3
"""Rebuild the four standalone SuperHost SVGs from editable vector components.

Usage: python3 source/rebuild.py [--export]
SVG assembly uses the Python standard library. --export additionally requires
the Inkscape command-line application to create transparent PNGs and vector PDFs.
"""
from pathlib import Path
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import argparse,json,subprocess,xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVG);ET.register_namespace('inkscape',INK)
def tag(t):return '{'+SVG+'}'+t

def component(filename):
    e=ET.parse(HERE/'components'/filename).getroot()
    if e.tag.split('}')[-1]=='svg':
        return deepcopy(next(child for child in e if child.tag.split('}')[-1]=='g'))
    return deepcopy(e)

def layer(root,ident,label,transform=''):
    attrs={'id':ident,'{'+INK+'}groupmode':'layer','{'+INK+'}label':label}
    if transform:attrs['transform']=transform
    return ET.SubElement(root,tag('g'),attrs)

def build():
    cfg=json.loads((HERE/'construction.json').read_text())
    flag=json.loads((HERE/'pofbc/flag-paths.json').read_text())
    assert len(flag)==12
    out=ROOT/'svg';out.mkdir(exist_ok=True)
    files=[]
    for name,layout in cfg['layouts'].items():
        for colour in (False,True):
            style='Colour' if colour else 'Black'
            root=ET.Element(tag('svg'),{
                'version':'1.1','width':str(layout['width']),'height':str(layout['height']),
                'viewBox':layout['viewBox'],'color':'#000000','fill':'#000000',
                'role':'img','aria-labelledby':'title description',
            })
            ET.SubElement(root,tag('title'),{'id':'title'}).text=f'SuperHost — {layout["title"]} — {style.lower()} reconstruction'
            ET.SubElement(root,tag('desc'),{'id':'description'}).text=(
                'Expect the most. SuperHost. Reconstructed from the historical reference with twelve unchanged '
                'PofBC flag paths, analytic star primitives, and custom letterforms. '
                'All artwork is editable vector geometry. No embedded raster or font dependency. '
                +(cfg['palette_note'] if colour else 'Single-colour artwork.'))
            ET.SubElement(root,tag('metadata')).text=json.dumps({
                'source':'https://projects.ahmadjalil.com/PofBC/',
                'commit':cfg['source_commit'],
                'reference':'https://ised-isde.canada.ca/cipo/trademark-search/0904301?lang=eng',
                'status':'Historical reconstruction, not a recovered original master',
                'layout':name,'date':cfg['date'],
            },ensure_ascii=False)
            layer(root,'layer-stars','01 · Star spray').append(component(layout['stars']))
            fg=layer(root,'layer-flag','02 · PofBC flag',layout['flag_transform'])
            for i,p in enumerate(flag):
                ET.SubElement(fg,tag('path'),{'id':f'flag-path-{i+1:02}',
                    'd':p['d'],'fill':p['fill'] if colour else '#000000',
                    'data-source-fill':p['fill']})
            layer(root,'layer-slogan','03 · Expect the most',layout['slogan_transform']).append(component('Slogan.svg'))
            layer(root,'layer-wordmark','04 · SuperHost',layout['wordmark_transform']).append(component('Wordmark.svg'))
            # Normalise SVG element namespaces, including reusable fragment roots.
            for e in root.iter():
                if not e.tag.startswith('{'):e.tag=tag(e.tag)
            ET.indent(root,space='  ')
            path=out/f'SuperHost_{name}_{style}{cfg.get("filename_suffix", "")}.svg'
            ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
            files.append(path)
    return files

def export(path):
    (ROOT/'pdf').mkdir(exist_ok=True);(ROOT/'preview').mkdir(exist_ok=True)
    jobs=[['inkscape',str(path),'--export-type=pdf',f'--export-filename={ROOT/"pdf"/(path.stem+".pdf")}'],
          ['inkscape',str(path),'--export-height=1800',f'--export-filename={ROOT/"preview"/(path.stem+".png")}']]
    for cmd in jobs:
        p=subprocess.run(cmd,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--export',action='store_true');args=parser.parse_args()
    files=build()
    if args.export:
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(export,files))
    print('\n'.join(str(path) for path in files))
