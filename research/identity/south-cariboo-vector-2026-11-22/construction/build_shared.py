"""Build exactly one authored tree master and a linked smaller pale instance.

The builder uses no bitmap and performs no raster contour extraction.
Run from any directory. Requires Python3 and Inkscape on PATH.
"""
from pathlib import Path
import copy,json,subprocess,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
CONSTRUCTION=HERE if (HERE/'shared-tree-model.json').exists() else HERE/'selected/construction'
OUT=CONSTRUCTION.parent
NS='http://www.w3.org/2000/svg';XLINK='http://www.w3.org/1999/xlink';INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',NS);ET.register_namespace('xlink',XLINK);ET.register_namespace('inkscape',INK)
def svg():return ET.Element('{'+NS+'}svg',viewBox='0 0 315 141',width='315',height='141',version='1.1')
def write(root,path):
    ET.indent(root,space='  ');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def run(args):
    r=subprocess.run(args,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr)
def master_flat(model):
    r=svg()
    for i,(name,d) in enumerate(model['master']['ink'].items()):ET.SubElement(r,'{'+NS+'}path',id='ink'+str(i),d=d,fill='black')
    ET.SubElement(r,'{'+NS+'}path',id='cuts',d=' '.join(model['master']['voids'].values()),fill='black')
    source=CONSTRUCTION/'master-boolean.svg';dest=CONSTRUCTION/'master-flat.svg';write(r,source)
    ids=','.join('ink'+str(i) for i in range(len(model['master']['ink'])))
    actions=f'select-by-id:{ids};path-union;object-set-attribute:id,merged;select-clear;select-by-id:merged,cuts;path-difference;object-set-attribute:id,master-ink;export-filename:{dest};export-text-to-path;export-do'
    run(['inkscape',str(source),'--export-type=svg','--export-plain-svg','--actions='+actions])
    paths=[]
    for e in ET.parse(dest).getroot():
        if e.tag=='{'+NS+'}path':
            e=copy.deepcopy(e);e.attrib.pop('style',None);e.attrib.pop('fill',None);paths.append(e)
    source.unlink();assert paths
    return paths
def add_letters(root,model):
    word=ET.SubElement(root,'{'+NS+'}g',id='wordmark',fill=model['colours']['dark'])
    for e in ET.parse(CONSTRUCTION/'lettering-outlined.svg').getroot():
        if e.tag.split('}')[-1] not in ('title','desc','metadata'):word.append(copy.deepcopy(e))
def build_root(model,paths,editable=False):
    r=svg();ET.SubElement(r,'{'+NS+'}title').text='South Cariboo Community Health Council — one shared tree master'
    ET.SubElement(r,'{'+NS+'}desc').text='The visible dark tree is the original SVG master. The pale tree is a linked use of exactly that geometry at five-sixths scale. Edit the master to update both. No independent pale shapes or raster images.'
    ET.SubElement(r,'{'+NS+'}metadata').text=json.dumps(model['metadata'])
    if editable:
        defs=ET.SubElement(r,'{'+NS+'}defs');mask=ET.SubElement(defs,'{'+NS+'}mask',id='master-cuts',maskUnits='userSpaceOnUse',x='0',y='0',width='315',height='141')
        ET.SubElement(mask,'{'+NS+'}rect',x='0',y='0',width='315',height='141',fill='white')
        for name,d in model['master']['voids'].items():ET.SubElement(mask,'{'+NS+'}path',id='cut-'+name,d=d,fill='black')
    trees=ET.SubElement(r,'{'+NS+'}g',id='tree-emblem')
    s=model['pale_instance']['scale'];tx,ty=model['pale_instance']['translate']
    use=ET.SubElement(trees,'{'+NS+'}use',id='pale-tree-linked',href='#tree-master',fill=model['colours']['pale'],transform=f'matrix({s} 0 0 {s} {tx} {ty})')
    use.set('{'+XLINK+'}href','#tree-master');use.set('{'+INK+'}label','Pale tree — linked copy of dark master')
    # Fill lives on the wrapper so the clone can inherit its own pale fill.
    dark=ET.SubElement(trees,'{'+NS+'}g',id='dark-tree-colour',fill=model['colours']['dark'])
    dx,dy,sx,sy=model['master']['alignment_dx_dy_sx_sy']
    master=ET.SubElement(dark,'{'+NS+'}g',id='tree-master',transform=f'matrix({sx} 0 0 {sy} {dx} {dy})')
    master.set('{'+INK+'}label','TREE MASTER — edit this shape to update both trees')
    if editable:
        master.set('mask','url(#master-cuts)')
        for name,d in model['master']['ink'].items():ET.SubElement(master,'{'+NS+'}path',id='branch-'+name,d=d)
    else:
        for path in paths:master.append(copy.deepcopy(path))
    add_letters(r,model)
    return r
def expand(root):
    out=copy.deepcopy(root);master=out.find(f'.//{{{NS}}}g[@id="tree-master"]');trees=out.find(f'.//{{{NS}}}g[@id="tree-emblem"]')
    use=trees.find('{'+NS+'}use');i=list(trees).index(use)
    clone=ET.Element('{'+NS+'}g',id='pale-tree-expanded',fill=use.get('fill'),transform=use.get('transform'))
    g=copy.deepcopy(master)
    for el in g.iter():el.attrib.pop('id',None)
    clone.append(g);trees.remove(use);trees.insert(i,clone)
    out.find('{'+NS+'}desc').text='Expanded compatibility export of the linked shared-tree master. Geometry matches exactly; this export does not retain a live clone relationship.'
    return out
def render(svgpath,dest,width,bg=None):
    args=['inkscape',str(svgpath),'--export-type=png','--export-width='+str(width),'--export-filename='+str(dest)]
    if bg:args.append('--export-background='+bg)
    run(args)
def main():
    model=json.loads((CONSTRUCTION/'shared-tree-model.json').read_text());paths=master_flat(model)
    root=build_root(model,paths)
    main_svg=OUT/'South_Cariboo_Reconstructed.svg';write(root,main_svg)
    write(expand(root),OUT/'South_Cariboo_Expanded.svg')
    write(build_root(model,paths,editable=True),CONSTRUCTION/'South_Cariboo_Branch_Model.svg')
    master_only=svg();master_only.set('viewBox','0 0 76 141');master_only.set('width','76')
    master_only.set('fill',model['colours']['dark'])
    master_only.append(copy.deepcopy(root.find(f'.//{{{NS}}}g[@id="tree-master"]')))
    write(master_only,OUT/'South_Cariboo_Tree_Master.svg')
    render(main_svg,OUT/'South_Cariboo_Preview.png',1890,'white')
    render(main_svg,OUT/'South_Cariboo_Transparent.png',2520)
    run(['inkscape',str(main_svg),'--export-type=pdf','--export-filename='+str(OUT/'South_Cariboo_Vector.pdf')])
    print('Built one editable master, one linked pale instance, expanded compatibility SVG, PDF and PNG exports.')
if __name__=='__main__':main()
