"""Preserve selected PDF vector paths as SVG, without rasterization or tracing."""
import copy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import fitz

BASE=Path(__file__).resolve().parent
SOURCE=BASE/'current-crown-sources'
OUT=BASE/'current-crown-vectors'
OUT.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')

def extract(name,source,page,indices,note):
    doc=fitz.open(SOURCE/source)
    p=doc[page]
    drawings=p.get_drawings()
    original=ET.fromstring(p.get_svg_image())
    leaves=[]
    def walk(node):
        for child in node:
            if child.tag==f'{{{NS}}}defs': continue
            if child.tag==f'{{{NS}}}path': leaves.append(child)
            walk(child)
    walk(original)
    assert len(leaves)==len(drawings),(source,len(leaves),len(drawings))
    keep={id(leaves[i]) for i in indices}
    def selected(node):
        if node.tag==f'{{{NS}}}path': return copy.deepcopy(node) if id(node) in keep else None
        if node.tag not in (f'{{{NS}}}g', f'{{{NS}}}svg'): return None
        new=ET.Element(node.tag,node.attrib)
        for child in node:
            chosen=selected(child)
            if chosen is not None:new.append(chosen)
        return new if len(new) else None
    output=selected(original)
    rect=fitz.Rect(drawings[indices[0]]['rect'])
    for i in indices[1:]: rect|=drawings[i]['rect']
    rect=rect+(-.6,-.6,.6,.6)
    output.set('viewBox',' '.join(f'{v:.6f}' for v in (rect.x0,rect.y0,rect.width,rect.height)))
    output.set('width',f'{rect.width:.6f}')
    output.set('height',f'{rect.height:.6f}')
    refs=set(re.findall(r'url\(#([^\)]+)\)',ET.tostring(output,encoding='unicode')))
    definitions={el.get('id'):el for defs in original.findall(f'{{{NS}}}defs') for el in defs if el.get('id')}
    added=set();needed=ET.Element(f'{{{NS}}}defs')
    while refs-added:
        key=sorted(refs-added)[0]
        assert key in definitions, key
        node=copy.deepcopy(definitions[key]);needed.append(node);added.add(key)
        refs.update(re.findall(r'url\(#([^\)]+)\)',ET.tostring(node,encoding='unicode')))
    if len(needed):output.insert(0,needed)
    assert not output.findall(f'.//{{{NS}}}image')
    assert not output.findall(f'.//{{{NS}}}text')
    assert not output.findall(f'.//{{{NS}}}use')
    data=ET.tostring(output,encoding='utf-8',xml_declaration=True)
    path=OUT/(name+'.svg');path.write_bytes(data)
    return dict(id=name,sourceFile=str(SOURCE/source),sourceSha256=hashlib.sha256((SOURCE/source).read_bytes()).hexdigest(),sourcePage=page+1,selectedDrawingIndices=indices,crop=list(rect),pathCount=len(indices),imageCount=0,localFile=str(path),sha256=hashlib.sha256(data).hexdigest(),note=note,extraction='PyMuPDF PDF-to-SVG conversion, preserving exact selected source path nodes and all ancestor transforms; unrelated paths, text, raster images, and unused definitions removed. No tracing, type recreation, or recolouring.')

records=[]
records.append(extract('bcfma-2021-source-vector','bcfma-2021.pdf',0,list(range(170)),'Full teal emblem and grey wordmark from the official 2020/21 report cover.'))
records.append(extract('bcib-2022-horizontal-reversed-source-vector','bcib-boh-2022.pdf',0,list(range(2,45)),'Original reversed full-name horizontal logo, from the 2021/22 Building Opportunity Here report cover.'))
records.append(extract('bcib-2025-tagline-reversed-source-vector','bcib-boh-2025.pdf',0,list(range(29,35))+list(range(36,60)),'Original reversed Building Opportunity Here tagline lockup from 2024/25 report cover. Adjacent Respectful Onsite Initiative mark excluded.'))
records.append(extract('columbia-power-2024-reversed-source-vector','columbia-power-2024.pdf',76,list(range(3,28)),'Original pale-grey reversed mark from the back cover of the official 2024 history book; no invented full-colour conversion.'))
records.append(extract('infrastructure-bc-2026-colour-source-vector','infrastructure-bc-brochure-2026.pdf',12,list(range(11,76)),'Original full-colour logo from final page of Spring 2026 BC Major Infrastructure Projects Brochure.'))
records.append(extract('infrastructure-bc-2026-reversed-source-vector','infrastructure-bc-brochure-2026.pdf',0,list(range(12,76)),'Original white reversed logo from cover of Spring 2026 BC Major Infrastructure Projects Brochure.'))
records.append(extract('bccie-2022-source-vector','bccie-strategic-2022.pdf',0,list(range(3,58)),'Full BCCIE logo from the official 2022-2025 strategic plan; dated sighting, not an assertion of adoption date.'))
records.append(extract('community-living-bc-2023-colour-source-vector','clbc-strategic-2023.pdf',0,list(range(25,63)),'Full colour CLBC corporate logo from cover of official 2023 Strategic Plan Report.'))
records.append(extract('community-living-bc-2014-reversed-source-vector','clbc-2014.pdf',0,list(range(4,42)),'Original white reversed CLBC logo from official 2013-2014 annual report cover.'))
records.append(extract('bc-housing-research-centre-source-vector','bchousing-community-housing.pdf',0,list(range(9,45)),'Full BC Housing Research Centre subbrand lockup from the official Community Housing for Resilient Communities report cover.'))
records.append(extract('bc-housing-corporate-component-source-vector','bchousing-community-housing.pdf',0,list(range(10,31)),'Corporate emblem and BC HOUSING wordmark isolated from the Research Centre lockup; separator and RESEARCH CENTRE subtitle omitted. Exact source geometry preserved. This is an extracted component rather than a standalone official master file.'))
(OUT/'extraction-metadata.json').write_text(json.dumps(records,indent=2))
print(json.dumps([{'id':r['id'],'pathCount':r['pathCount'],'imageCount':r['imageCount'],'bytes':Path(r['localFile']).stat().st_size} for r in records]))
