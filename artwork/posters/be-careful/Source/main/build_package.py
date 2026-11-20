"""Assemble deliberately drawn components; export true vector artwork.

Requires Python 3, FontTools, Pillow, NumPy, SciPy, Inkscape and Poppler.
The vector geometry is authored in the three companion construction scripts.
Raster masks in the review step are only measurements; they never generate paths.
"""
from pathlib import Path
from copy import deepcopy
import base64, json, re, subprocess, xml.etree.ElementTree as ET
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

R = Path(__file__).resolve().parents[1]
E = R/'exports'; E.mkdir(exist_ok=True)
(R/'analysis').mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',NS); ET.register_namespace('inkscape',INK)
TAG=lambda s:f'{{{NS}}}{s}'
INK_COLOR='#525850'  # median interior RGB of the supplied scan; not a historical ink specification
BASE='BC_Forest_Service_1960'

def root_svg(title,desc):
 root=ET.Element(TAG('svg'),{'width':'1234','height':'909','viewBox':'0 0 1234 909','version':'1.1'})
 ET.SubElement(root,TAG('title')).text=title
 ET.SubElement(root,TAG('desc')).text=desc
 return root

def write(root,path):
 ET.indent(root)
 ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def render(path,destination,width=1234,bg=None):
 args=['inkscape',str(path),f'--export-filename={destination}',f'--export-width={width}']
 if bg:args += [f'--export-background={bg}','--export-background-opacity=1']
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr)

def matrix(text):
 t=Transform()
 for op,contents in re.findall(r'(translate|scale|matrix)\s*\(([^)]+)\)',text):
  a=[float(x) for x in re.split(r'[ ,]+',contents.strip())]
  if op=='translate': t=t.translate(a[0],a[1] if len(a)>1 else 0)
  elif op=='scale':t=t.scale(a[0],a[1] if len(a)>1 else a[0])
  else:t=t.transform(Transform(*a))
 return t

def flattened_paths(node,parent=Transform()):
 t=parent.transform(matrix(node.get('transform','')))
 if node.tag==TAG('path'):
  pen=SVGPathPen(None);parse_path(node.attrib['d'],TransformPen(pen,t));yield pen.getCommands()
 for child in node:yield from flattened_paths(child,t)

def assemble():
 master=root_svg('BC Forest Service - Be Careful - 1960 reconstruction',
  'Manually reconstructed forest and flame silhouette and custom outlined lettering. '
  'Five named editable layers; no embedded raster, automatic tracing, external fonts or linked assets. '
  'Original coordinate system 1234 by 909. Colour sampled from the scan, not a verified ink standard.')
 sil=ET.parse(R/'silhouette/silhouette.svg').getroot()
 outlines=ET.parse(R/'main/initials_footer.svg').getroot()
 lettering=ET.parse(R/'lettering/white_lettering.svg').getroot()
 layers=[
  ('forest-flame-silhouette','01 - Forest and flames',next(x for x in sil if x.tag==TAG('g'))),
  ('large-initials','02 - Large B and C',outlines.find(f".//*[@id='large-initials']")),
  ('be-careful-small-letters','03 - Be Careful small lettering',lettering.find(f".//*[@id='be-careful-small-letters']")),
  ('prevent-forest-fires','04 - Prevent Forest Fires',lettering.find(f".//*[@id='prevent-forest-fires']")),
  ('service-signature','05 - BC Forest Service',outlines.find(f".//*[@id='service-signature']"))]
 for id,label,g in layers:
  g=deepcopy(g);g.set('id',id);g.set(f'{{{INK}}}groupmode','layer');g.set(f'{{{INK}}}label',label)
  g.set('fill',INK_COLOR if id=='forest-flame-silhouette' else '#ffffff')
  g.set('fill-rule','evenodd');master.append(g)
 path=E/f'{BASE}_Master.svg';write(master,path)
 # White lettering union above silhouette; vector boolean difference creates true holes.
 k=root_svg('BC Forest Service - single colour with transparent lettering',
  'Single-colour vector reconstruction with true geometric knockouts. No masks, fonts or images.')
 ET.SubElement(k,TAG('path'),{'id':'ink-shape','fill':INK_COLOR,'fill-rule':'evenodd',
  'd':' '.join(flattened_paths(master.find(f".//*[@id='forest-flame-silhouette']")))})
 lettering_d=[]
 for group in list(master)[3:]:
  if group.tag==TAG('g'):lettering_d.extend(flattened_paths(group))
 ET.SubElement(k,TAG('path'),{'id':'lettering-cutout','fill':'#ffffff','fill-rule':'evenodd','d':' '.join(lettering_d)})
 boolean_input=R/'analysis/knockout_input.svg';write(k,boolean_input)
 out=E/f'{BASE}_Knockout.svg'
 cmd=['inkscape',str(boolean_input),'--export-text-to-path',
  '--actions',f'select-by-id:ink-shape,lettering-cutout;path-difference;export-area-page;export-filename:{out};export-text-to-path;export-do']
 p=subprocess.run(cmd,capture_output=True,text=True)
 if p.returncode or not out.exists():raise RuntimeError(p.stderr)
 # Remove editor metadata and publish a portable plain SVG containing final path geometry.
 raw=ET.parse(out).getroot()
 cleaned=root_svg('BC Forest Service - transparent knockout artwork',
  'Reconstructed single-colour artwork. Lettering is cut out of the filled outline; no white objects, masks or bitmap images.')
 for i,node in enumerate(raw.iter(TAG('path'))):
  n=deepcopy(node);n.set('id',f'ink-{i+1}');n.set('fill',INK_COLOR)
  n.set('fill-rule','evenodd');n.attrib.pop('style',None);cleaned.append(n)
 write(cleaned,out)
 for name,color in [('Black','#000000'),('White','#ffffff')]:
  variant=deepcopy(cleaned)
  for p in variant.iter(TAG('path')):p.set('fill',color)
  write(variant,E/f'{BASE}_{name}.svg')
 render(path,E/f'{BASE}_Preview.png',width=2468,bg='#ffffff')
 render(out,E/f'{BASE}_Transparent.png',width=4096)
 render(path,R/'analysis/master_1234.png',width=1234,bg='#ffffff')
 render(out,R/'analysis/knockout_1234.png',width=1234,bg='#ffffff')
 for suffix,source in [('Print.pdf',path),('Black.eps',E/f'{BASE}_Black.svg')]:
  p=subprocess.run(['inkscape',str(source),f'--export-filename={E/(BASE+"_"+suffix)}'],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(p.stderr)
 print(json.dumps({'master':str(path),'path_count':sum(1 for _ in master.iter(TAG('path'))),
  'layers':len(layers),'knockout_paths':sum(1 for _ in cleaned.iter(TAG('path')))}))
 return master

if __name__=='__main__':assemble()
