"""Fixed museum-cover labels; closest inspected typeface, not confirmed exact."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,html
P=Path(__file__).resolve().parent
def lookup(label):
 items=json.loads((P/'label_sources.json').read_text())
 for item in items:
  if label in [item['text'],item['slug']]:return item
 raise ValueError(f'Unsupported fixed label: {label}')
def measure_label(label):
 item=lookup(label);svg=ET.parse(P/item['svg']).getroot();x,y,w,h=map(float,svg.attrib['viewBox'].split());return {'width':w,'height':h,'viewBox':[x,y,w,h],'source':item}
def label_group(label,x=0,y=0,width=None,height=None,color='#163c36'):
 item=lookup(label);svg=ET.parse(P/item['svg']).getroot();vx,vy,w,h=map(float,svg.attrib['viewBox'].split())
 sx=width/w if width is not None else height/h if height is not None else 1
 sy=height/h if height is not None else sx
 path=svg.find('{http://www.w3.org/2000/svg}path').attrib['d']
 return f'<g aria-label="{html.escape(item["text"],quote=True)}" transform="translate({x:.6f} {y:.6f}) scale({sx:.9f} {sy:.9f}) translate({-vx:.6f} {-vy:.6f})"><path fill="{html.escape(color,quote=True)}" fill-rule="evenodd" d="{path}"/></g>'
