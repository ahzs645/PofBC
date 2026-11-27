"""Create print wrapper and visually reviewable exports for the final vector."""
from pathlib import Path
from copy import deepcopy
import json
from lxml import etree as ET

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output'
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'

def main():
    master=OUT/'provincial-library-archives.svg'
    tree=ET.parse(str(master));root=tree.getroot()
    patch=ROOT/'work'/'crown-backings.json'
    if patch.exists() and not root.xpath('//*[@id="crown-cap-backing"]'):
        group=ET.Element('{'+SVG+'}g',id='crown-cap-backing',attrib={'{'+INK+'}groupmode':'layer','{'+INK+'}label':'00 - Restored opaque crown-cap interiors'})
        for i,d in enumerate(json.loads(patch.read_text())['paths']):
            ET.SubElement(group,'{'+SVG+'}path',id=f'crown-cap-backing-{i+1}',d=d,fill='#ffffff')
        root.insert(3,group)
        desc=root.find('{'+SVG+'}desc')
        desc.text+=' White backings repair patchy transparency within the enclosed crown caps and central highlight of the supplied cutout; genuine exterior apertures remain transparent.'
        tree.write(master,xml_declaration=True,encoding='UTF-8',pretty_print=True)
    # A4 print page. Artwork is copied as paths, not rendered to a bitmap.
    pdfroot=ET.Element('{'+SVG+'}svg',nsmap={None:SVG},width='210mm',height='297mm',viewBox='0 0 210 297',version='1.1')
    ET.SubElement(pdfroot,'{'+SVG+'}title').text='Provincial Library & Archives - vector artwork'
    scale=186/1116
    top=(297-1410*scale)/2
    g=ET.SubElement(pdfroot,'{'+SVG+'}g',transform=f'translate(12 {top:.6f}) scale({scale:.9f})')
    for el in root:
        if ET.QName(el).localname in ('g','defs','path'):
            g.append(deepcopy(el))
    ET.ElementTree(pdfroot).write(ROOT/'work'/'print-a4.svg',xml_declaration=True,encoding='UTF-8',pretty_print=True)
    forbidden=root.xpath('//*[local-name()="image" or local-name()="text" or local-name()="foreignObject" or local-name()="filter"]')
    paths=root.xpath('//*[local-name()="path"]')
    ids=[el.get('id') for el in root.iter() if el.get('id')]
    assert not forbidden,'Unexpected raster, font dependency, or filter in SVG'
    assert len(ids)==len(set(ids)),'Duplicate element IDs'
    print(json.dumps({'svg':str(master),'paths':len(paths),'named_layers':len(root.xpath('//*[@inkscape:groupmode="layer"]',namespaces={'inkscape':INK})),'embedded_images':0,'font_dependencies':0,'duplicate_ids':0,'crown_cap_restorations':len(root.xpath('//*[@id="crown-cap-backing"]/*'))},indent=2))

if __name__=='__main__':main()
