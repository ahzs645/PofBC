"""Assemble hand-built lettering and constructed frames into production SVGs.

No image tracing or bitmap-to-path operation is used. Lettering is provided as
deliberately authored paths, and each frame is an outer/inner geometric ring.
"""
from pathlib import Path
from copy import deepcopy
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

def tag(name): return f'{{{NS}}}{name}'
def fmt(x): return f'{x:.4f}'.rstrip('0').rstrip('.')

def rounded_rect(x,y,w,h,r):
    """A closed rect made from four lines and four cubic quarter-rounds."""
    f=fmt
    if not r:
        return f'M{f(x)} {f(y)}H{f(x+w)}V{f(y+h)}H{f(x)}Z'
    k = 0.5522847498307936
    return (
        f'M{f(x+r)} {f(y)}H{f(x+w-r)}'
        f'C{f(x+w-r+k*r)} {f(y)} {f(x+w)} {f(y+r-k*r)} {f(x+w)} {f(y+r)}'
        f'V{f(y+h-r)}'
        f'C{f(x+w)} {f(y+h-r+k*r)} {f(x+w-r+k*r)} {f(y+h)} {f(x+w-r)} {f(y+h)}'
        f'H{f(x+r)}'
        f'C{f(x+r-k*r)} {f(y+h)} {f(x)} {f(y+h-r+k*r)} {f(x)} {f(y+h-r)}'
        f'V{f(y+r)}'
        f'C{f(x)} {f(y+r-k*r)} {f(x+r-k*r)} {f(y)} {f(x+r)} {f(y)}Z'
    )

GRID = {
    'serif-stacked': dict(xs=[184.75,373.75],ys=[279,453],w=173.5,h=156,tx=8.4,ty=5.6,r=0,ri=0),
    'symbol': dict(xs=[41,385],ys=[33,379],w=319,h=315,tx=9,ty=9,r=0,ri=0),
    'sans-stacked': dict(xs=[227.25,312.75],ys=[159.25,237.75],w=82,h=74.5,tx=6.5,ty=6.5,r=4.5,ri=1.5),
    'sans-horizontal': dict(xs=[85.5,143.5],ys=[106,160],w=56,h=52,tx=5.1,ty=5.1,r=4,ri=1.4),
}

ASSETS = [
    dict(key='serif-stacked', title='The Development Corporation — serif stacked logo',
         reference='460346.png', canvas=(751,639), crop=(10,20,738,599),
         lettering='source/serif-lettering.svg'),
    dict(key='symbol', title='The Development Corporation — sharp-corner symbol',
         reference='494945.png', canvas=(755,740), crop=(23,15,699,697),lettering=None),
    dict(key='sans-stacked', title='The Development Corporation — sans-serif stacked logo',
         reference='901351.png', canvas=(640,350), crop=(142,35,345,287),
         lettering='source/sans-stacked-lettering.svg'),
    dict(key='sans-horizontal', title='The Development Corporation — sans-serif horizontal logo',
         reference='901352.png', canvas=(640,350), crop=(75,96,511,126),
         lettering='source/sans-horizontal-lettering.svg'),
]

GRID = json.loads((OUT/'source'/'frame-construction.json').read_text())

def frame_group(key):
    p=GRID[key]
    group=ET.Element(tag('g'),{'id':'four-panel-symbol','fill-rule':'evenodd'})
    for row,y in enumerate(p['ys']):
        for col,x in enumerate(p['xs']):
            d=rounded_rect(x,y,p['w'],p['h'],p['r'])+' '+rounded_rect(x+p['tx'],y+p['ty'],p['w']-2*p['tx'],p['h']-2*p['ty'],p['ri'])
            ET.SubElement(group,tag('path'),{'id':f'panel-{row+1}-{col+1}','d':d})
    return group

def load_lettering(path):
    root=ET.parse(path).getroot()
    group=ET.Element(tag('g'),{'id':'lettering'})
    for child in root:
        if child.tag.rsplit('}',1)[-1] in ('title','desc','metadata'): continue
        c=deepcopy(child)
        for el in c.iter():
            if el.get('fill') in ('black','#000','#000000'): el.attrib.pop('fill')
            if el.get('id')=='lettering': el.set('id','glyph-outlines')
        group.append(c)
    # The final deliverable must contain only intentional vector shapes.
    assert not any(e.tag.rsplit('}',1)[-1] in ('image','text','foreignObject') for e in group.iter())
    return group

def write_svg(asset,aligned=False,white=False):
    key=asset['key']
    v=(0,0,*asset['canvas']) if aligned else asset['crop']
    root=ET.Element(tag('svg'),{'width':fmt(v[2]),'height':fmt(v[3]),'viewBox':' '.join(map(fmt,v)),
                              'role':'img','aria-labelledby':'title description','version':'1.1'})
    ET.SubElement(root,tag('title'),{'id':'title'}).text=asset['title']
    ET.SubElement(root,tag('desc'),{'id':'description'}).text=(
        'Clean vector reconstruction from the user-supplied reference. '
        'Custom, manually constructed lettering; geometric frames. '
        'All lettering is paths, with no font or raster image dependency. '
        'The historical typeface has not been authenticated.'
    )
    art=ET.SubElement(root,tag('g'),{'id':'artwork','fill':'#ffffff' if white else '#000000'})
    if asset['lettering']: art.append(load_lettering(ROOT/asset['lettering']))
    art.append(frame_group(key))
    folder=OUT/('reference-aligned' if aligned else 'svg')
    folder.mkdir(parents=True,exist_ok=True)
    filename=f'development-corporation-{key}'+('-white' if white else '')+'.svg'
    ET.indent(root,space='  ')
    file=folder/filename
    ET.ElementTree(root).write(file,encoding='utf-8',xml_declaration=True)
    return file

def main():
    for a in ASSETS:
        for aligned,white in ((False,False),(True,False),(False,True)):
            write_svg(a,aligned=aligned,white=white)
    (OUT/'source').mkdir(parents=True,exist_ok=True)
    (OUT/'source'/'frame-construction.json').write_text(json.dumps(GRID,indent=2)+'\n')
    print(json.dumps({'svg_files':12,'assets':[a['key'] for a in ASSETS]},indent=2))

if __name__=='__main__': main()
