#!/usr/bin/env python3
"""Reassemble this vector artwork from its authored SVG components.

Python standard library only. Add --export to run Inkscape for PDF and PNG.
No source bitmap is opened or traced, and no font is required.
"""
from pathlib import Path
import sys,subprocess,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
NS='http://www.w3.org/2000/svg';INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',NS);ET.register_namespace('inkscape',INK)
root=ET.Element('{'+NS+'}svg',{'width':'1354','height':'1161','viewBox':'0 0 1354 1161','version':'1.1'})
ET.SubElement(root,'{'+NS+'}title').text='GO B.C. FERRIES — reconstructed vector sticker'
palette={'#ffe9aa':'#fce6a3','#1b9fa8':'#1da4a9','#00272c':'#031e24','#0b1211':'#070a09','#007638':'#047634','#0b0f0b':'#070a09','#1da1a7':'#1da4a9'}
labels={'border-and-field':'01 · Border and teal field','mountains':'02 · Mountains and snow','ferry-illustration':'03 · Ferry','gull':'04 · Gull','perimeter-text':'05 · Route lettering','go-bc-ferries':'06 · Main title','subtitle':'07 · Authority subtitle','dogwood-flag':'08 · Dogwood flag','perimeter-dots':'09 · Separators'}
for name in ['base.svg','ferry.svg','gull.svg','lettering.svg','flag.svg']:
    for el in ET.parse(BASE/'components'/name).getroot():
        if el.tag.split('}')[-1] not in ['g','defs']:continue
        if el.tag.split('}')[-1]=='g':
            el.set('{'+INK+'}groupmode','layer');el.set('{'+INK+'}label',labels.get(el.get('id'),el.get('id','Artwork')))
        for node in el.iter():
            for k,v in list(node.attrib.items()):
                for old,new in palette.items():v=v.replace(old,new)
                node.set(k,v)
        root.append(el)
dest=BASE/'go-bc-ferries-rebuilt.svg';ET.ElementTree(root).write(dest,encoding='utf-8',xml_declaration=True)
print(dest)
if '--export' in sys.argv:
    for ext in ['pdf','png']:
        subprocess.run(['inkscape',str(dest),'--export-type='+ext,'--export-filename='+str(BASE/('go-bc-ferries-rebuilt.'+ext))],check=True)
