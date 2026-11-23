"""Rebuild the portable logo from authored branch geometry and outlined lettering.
Run: python3 construction/assemble_logo.py [--export]
With --export, also writes white PNG, transparent PNG and vector PDF.
No bitmap is consulted by this build; all geometry comes from JSON and SVG components.
"""
from pathlib import Path
import json,copy,subprocess,sys,xml.etree.ElementTree as ET
from build_trees import rebuild,svg,HERE,NS
OUT=HERE.parent
model,fit=rebuild();rt=svg()
ET.SubElement(rt,'{'+NS+'}title').text='South Cariboo Community Health Council - reconstructed logo'
ET.SubElement(rt,'{'+NS+'}desc').text='Reconstructed using manually authored branch tiers and openings, plus fitted native typeface contours. No automatic tracing or raster contour extraction.'
tree=ET.SubElement(rt,'{'+NS+'}g',id='tree-emblem')
for key in ['pale','dark']:
 dx,dy,sx,sy=fit[key]['matrix_parameters_dx_dy_sx_sy'];g=ET.SubElement(tree,'{'+NS+'}g',id=key+'-tree-alignment',transform=f'matrix({sx} 0 0 {sy} {dx} {dy})')
 for e in ET.parse(HERE/(key+'-flat.svg')).getroot():
  if e.tag=='{'+NS+'}path':g.append(copy.deepcopy(e))
letters=ET.SubElement(rt,'{'+NS+'}g',id='wordmark',fill=model['colors']['dark'])
for e in ET.parse(HERE/'lettering-outlined.svg').getroot():
 if e.tag.split('}')[-1] not in ['title','desc','metadata']:letters.append(copy.deepcopy(e))
ET.SubElement(rt,'{'+NS+'}metadata').text=json.dumps(json.loads((HERE/'reconstruction-metadata.json').read_text()),ensure_ascii=False)
ET.indent(rt,space='  ');dest=OUT/'South_Cariboo_Reconstructed.svg';ET.ElementTree(rt).write(dest,encoding='utf-8',xml_declaration=True)
if '--export' in sys.argv:
 for name,width,bg in [('South_Cariboo_Preview.png',1890,'white'),('South_Cariboo_Transparent.png',2520,None)]:
  args=['inkscape',str(dest),'--export-type=png','--export-width='+str(width),'--export-filename='+str(OUT/name)]
  if bg:args.append('--export-background='+bg)
  subprocess.run(args,check=True,capture_output=True)
 subprocess.run(['inkscape',str(dest),'--export-type=pdf','--export-filename='+str(OUT/'South_Cariboo_Vector.pdf')],check=True,capture_output=True)
print(dest)
