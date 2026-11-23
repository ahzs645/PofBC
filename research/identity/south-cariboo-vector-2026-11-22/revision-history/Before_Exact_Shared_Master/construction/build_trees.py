"""Rebuild the refined tree paths from named authored components, not from a bitmap.
Requires Python3 and Inkscape on PATH. Run this file or assemble_logo.py.
The editable source of truth is tree-geometry.json beside this script.
"""
from pathlib import Path
import json,copy,subprocess,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
NS='http://www.w3.org/2000/svg';INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',NS);ET.register_namespace('inkscape',INK)
def svg():return ET.Element('{'+NS+'}svg',viewBox='0 0 315 141',width='315',height='141',version='1.1')
def rebuild():
 model=json.loads((HERE/'tree-geometry.json').read_text());fit=json.loads((HERE/'alignment-fit.json').read_text())
 for key in ['pale','dark']:
  rt=svg();colour=model['colors'][key]
  for i,(name,d) in enumerate(model[key].items()):ET.SubElement(rt,'{'+NS+'}path',id=f'ink{i}',d=d,fill=colour)
  ET.SubElement(rt,'{'+NS+'}path',id='holes',d=' '.join(model[key+'_voids'].values()),fill='black')
  src=HERE/(key+'-boolean.svg');ET.ElementTree(rt).write(src,encoding='utf-8',xml_declaration=True)
  dest=HERE/(key+'-flat.svg');ids=','.join('ink'+str(i) for i in range(len(model[key])))
  actions=f'select-by-id:{ids};path-union;object-set-attribute:id,merged;select-clear;select-by-id:merged,holes;path-difference;object-set-attribute:id,{key}-tree;export-filename:{dest};export-text-to-path;export-do'
  result=subprocess.run(['inkscape',str(src),'--export-plain-svg','--export-type=svg','--actions='+actions],capture_output=True,text=True)
  if result.returncode:raise RuntimeError(result.stderr)
  flat=ET.parse(dest)
  for e in flat.getroot():
   if e.tag=='{'+NS+'}path':e.attrib.pop('style',None);e.set('fill',colour)
  flat.write(dest,encoding='utf-8',xml_declaration=True)
  src.unlink()
 edit=svg();ET.SubElement(edit,'{'+NS+'}title').text='South Cariboo - refined editable branch construction'
 ET.SubElement(edit,'{'+NS+'}desc').text='Named branches and ink breaks from tree-geometry.json. No raster tracing. Glyphs are outlined.'
 defs=ET.SubElement(edit,'{'+NS+'}defs')
 for key in ['pale','dark']:
  mask=ET.SubElement(defs,'{'+NS+'}mask',id=key+'-breaks',maskUnits='userSpaceOnUse',x='0',y='0',width='315',height='141')
  ET.SubElement(mask,'{'+NS+'}rect',width='315',height='141',fill='white')
  for n,d in model[key+'_voids'].items():ET.SubElement(mask,'{'+NS+'}path',id=key+'-void-'+n,d=d,fill='black')
 for key in ['pale','dark']:
  dx,dy,sx,sy=fit[key]['matrix_parameters_dx_dy_sx_sy']
  g=ET.SubElement(edit,'{'+NS+'}g',id=key+'-tree',fill=model['colors'][key],mask='url(#'+key+'-breaks)',transform=f'matrix({sx} 0 0 {sy} {dx} {dy})')
  g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',key.title()+' tree - editable branches')
  for n,d in model[key].items():ET.SubElement(g,'{'+NS+'}path',id=key+'-'+n,d=d)
 word=ET.SubElement(edit,'{'+NS+'}g',id='wordmark',fill=model['colors']['dark'])
 for e in ET.parse(HERE/'lettering-outlined.svg').getroot():
  if e.tag.split('}')[-1] not in ['title','desc','metadata']:word.append(copy.deepcopy(e))
 ET.indent(edit,space='  ');ET.ElementTree(edit).write(HERE/'South_Cariboo_Branch_Model.svg',encoding='utf-8',xml_declaration=True)
 return model,fit
if __name__=='__main__':rebuild();print('Updated flat tree paths and editable branch model.')
