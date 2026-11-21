#!/usr/bin/env python3
"""Assemble the BC Forest Service emblem from editable, designed vector parts.
No bitmap contour tracing, raster images, or font dependencies are used in the master.
"""
from pathlib import Path
from copy import deepcopy
import json, argparse
from xml.etree import ElementTree as E

ROOT=Path(__file__).resolve().parent
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
E.register_namespace('', SVG)
E.register_namespace('inkscape', INK)
Q=lambda t:'{'+SVG+'}'+t
OUT=ROOT.parent
OUT.mkdir(parents=True,exist_ok=True)
P={'charcoal':'#30312d','trim':'#e6dfc9','olive':'#cecf8f','sky':'#f2df83','forest':'#203f34','foliage':'#659451','snow':'#faf3e0','shadow':'#c6c8b8','water':'#ccd7c7'}

def element(parent,tag,**attrs):
 return E.SubElement(parent,Q(tag),{k.replace('_','-'):str(v) for k,v in attrs.items()})
def layer(parent,id,label):
 g=element(parent,'g',id=id)
 g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',label)
 return g

def dpath(ctrl):
 n=lambda p:f'{p[0]:.2f},{p[1]:.2f}'
 return 'M '+n(ctrl[0])+' '+' '.join('C '+' '.join(n(q) for q in ctrl[i:i+3]) for i in range(1,13,3))+' Z'

inner=json.loads((ROOT/'geometry/inner_controls.json').read_text())
inner_d=dpath(inner)

def load_component(path):
 if not path.exists():return None
 item=E.parse(str(path)).getroot()
 def namespace(e):
  if isinstance(e.tag,str) and not e.tag.startswith('{'):e.tag=Q(e.tag)
  for child in e:namespace(child)
 namespace(item)
 if item.tag.rsplit('}',1)[-1]=='svg':
  group=E.Element(Q('g'))
  for child in list(item):
   if child.tag.rsplit('}',1)[-1] not in ('title','desc','metadata','namedview'):group.append(deepcopy(child))
  return group
 return deepcopy(item)

def build(aligned=False):
 svg=E.Element(Q('svg'),version='1.1',width='200mm',height=f'{1736/1330*200:.4f}mm',viewBox='155 152 1330 1736',role='img')
 svg.set('aria-labelledby','art-title art-description')
 if aligned:
  svg.set('width','1709');svg.set('height','2048');svg.set('viewBox','0 0 1709 2048')
 element(svg,'title',id='art-title').text='Forest Service - British Columbia: reconstructed vector emblem'
 element(svg,'desc',id='art-description').text='Recreated from the supplied image using geometric oval borders, font-derived outlined lettering, and hand-authored tree and landscape paths. All visible artwork is vector. The artboard outside the emblem is transparent.'
 defs=element(svg,'defs')
 clip=element(defs,'clipPath',id='landscape-window',clipPathUnits='userSpaceOnUse')
 element(clip,'path',d=inner_d)
 borders=layer(svg,'layer-border','01 - Outer oval, cream trim and olive band')
 border_models=json.loads((ROOT/'geometry/border_models.json').read_text())
 for model,fill,id in zip(border_models,[P['trim'],P['olive']],['outer-border-and-cream-trim','olive-band-and-inner-border']):
  element(borders,'path',id=id,d=dpath(model['centerline_controls']),fill=fill,stroke=P['charcoal'],stroke_width=model['stroke_width'],stroke_linejoin='round')
 sky=layer(svg,'layer-sky','02 - Golden sky')
 element(sky,'path',id='golden-sky',d=inner_d,fill=P['sky'])
 scene=layer(svg,'layer-landscape','03 - Mountains, shore, lake and foreground')
 scene.set('clip-path','url(#landscape-window)')
 frag=load_component(ROOT/'components/landscape.svg')
 if frag is not None:scene.append(frag)
 tree=layer(svg,'layer-tree','04 - Central evergreen and trunk')
 tree.set('clip-path','url(#landscape-window)')
 frag=load_component(ROOT/'components/central-tree.svg')
 if frag is not None:tree.append(frag)
 rim=layer(svg,'layer-medallion-outline','05 - Interior oval boundary')
 element(rim,'path',id='interior-outline',d=inner_d,fill='none',stroke=P['charcoal'],stroke_width='11',stroke_linejoin='round')
 letters=layer(svg,'layer-lettering','06 - Outlined lettering')
 frag=load_component(ROOT/'components/lettering.svg')
 if frag is not None:letters.append(frag)
 dots=layer(svg,'layer-separators','07 - Side separator dots')
 element(dots,'circle',id='left-separator',cx='318.5',cy='1107.7',r='15.4',fill=P['charcoal'])
 element(dots,'circle',id='right-separator',cx='1340',cy='1079.2',r='15.3',fill=P['charcoal'])
 return E.ElementTree(svg)

if __name__=='__main__':
 tree=build()
 E.indent(tree,space='  ')
 destination=OUT/'Forest_Service_BC_Reconstructed.svg'
 tree.write(destination,xml_declaration=True,encoding='UTF-8')
 print(destination)
