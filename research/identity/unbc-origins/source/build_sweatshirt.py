#!/usr/bin/env python3
"""Interpretive sweater lettering from the partly visible campaign photograph.
Uses custom collegiate geometry from build_campaign.py, never pixel tracing.
"""
from pathlib import Path
from math import sin,cos,radians
import json,subprocess
from xml.etree import ElementTree as ET
from build_campaign import COLLEGE,poly,fmt,word,save,OUT,HERE
BURGUNDY='#733E4A'
text='INTERIOR'; gap=22
full=sum(COLLEGE[c][0] for c in text)+gap*(len(text)-1)
cur=0;items=[]
for i,ch in enumerate(text):
 gw,polygons=COLLEGE[ch]
 angle=198+(cur+gw/2)/full*144
 rad=radians(angle);bx=550+400*cos(rad);by=600+400*sin(rad)
 parts=[]
 for j,p in enumerate(polygons):
  d=poly([((xx-gw/2)*1.19,(yy-100)*1.4) for xx,yy in p])
  parts.append(f'<path id="sweater-{i+1}-{ch}-{j+1}" d="{d}"/>')
 items.append(f'<g id="arched-letter-{i+1}-{ch}" transform="translate({fmt(bx)} {fmt(by)}) rotate({fmt(angle+90)})">'+''.join(parts)+'</g>')
 cur+=gw+gap
body=f'<g id="arched-interior-outline" aria-label="INTERIOR" fill="none" stroke="{BURGUNDY}" stroke-width="5.5" stroke-linejoin="miter">'+''.join(items)+'</g>'
body+=word('UNIVERSITY','NimbusRoman-Bold',105,663,890,96,color=BURGUNDY,ident='inferred-university-line')
p=save('interior-university-sweatshirt-interpretive',1100,820,'Interior University sweatshirt lettering - interpretive reconstruction','Interpretive reconstruction from the sweatshirt in the background photograph in IMG_7953(1).jpeg. The arched outlined word INTERIOR is visible; the lower UNIVERSITY line is partly concealed by folds and is completed by inference. Custom collegiate geometry and fitted serif outlines represent the visible style. The exact lower lettering, typeface, curve, proportions and print colour cannot be established from this small oblique source. This is a separate optional adaptation, not verified original artwork.',body)
expanded=p.with_name(p.stem+'-expanded.svg')
subprocess.run(['inkscape',str(p),'--export-plain-svg','--export-type=svg','--export-filename='+str(expanded),'--actions=select-all:all;object-stroke-to-path'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(expanded)
for el in tree.iter():
 if el.get('id')=='arched-interior-outline':
  for key in list(el.attrib):
   if key.startswith('stroke'):el.attrib.pop(key)
  el.set('fill',BURGUNDY)
tree.write(p,encoding='utf-8',xml_declaration=True);expanded.unlink()
meta={'file':p.name,'source':['IMG_7953(1).jpeg'],'construction':'Arched custom collegiate-outline INTERIOR, each letter individually positioned and expanded to filled paths; lower UNIVERSITY completed by inference in outlined serif lettering','font_approximation':['NimbusRoman-Bold for lower line'],'palette':{'interpretive_burgundy':BURGUNDY},'uncertainties':['Partial and small photographic evidence','Lower word is partly occluded and completed by inference','Exact collegiate forms, arc, proportions and colour unconfirmed'],'status':'interpretive adaptation - partial evidence'}
(HERE/'sweatshirt_metadata.json').write_text(json.dumps(meta,indent=2))
print(p)
