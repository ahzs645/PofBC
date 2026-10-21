"""Assemble authored vector components without image tracing or alignment fitting."""
from pathlib import Path
from lxml import etree as E
import hashlib, json
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
INKSCAPE='http://www.inkscape.org/namespaces/inkscape'
root=E.Element('{'+NS+'}svg',nsmap={None:NS,'inkscape':INKSCAPE})
root.attrib.update({'viewBox':'0 0 1305 1206','width':'1305','height':'1206','version':'1.1','role':'img','aria-labelledby':'artwork-title artwork-description'})
title=E.SubElement(root,'{'+NS+'}title',id='artwork-title')
title.text='Queen of Sidney - British Columbia Ferries sticker reconstruction'
desc=E.SubElement(root,'{'+NS+'}desc',id='artwork-description')
desc.text='Editable manually constructed vector artwork based on the supplied vintage sticker. All lettering is outlined. Flat colours replace paper grain and photographic lighting; the exterior is transparent. Source coordinate canvas: 1305 by 1206. No embedded bitmap or auto-traced contour data.'
for filename in ('scene-back.svg','ferry.svg','scene-front.svg','lettering.svg'):
    source=E.parse(str(ROOT/'src'/filename)).getroot()
    for child in source:
        if not isinstance(child.tag,str) or E.QName(child).localname in ('title','desc','metadata'):
            continue
        if child.get('id') in ('ferry','lettering'):
            child.set('{'+INKSCAPE+'}groupmode','layer')
            child.set('{'+INKSCAPE+'}label','06 Ferry' if child.get('id')=='ferry' else '10 Outlined lettering')
        root.append(child)
ids=[e.get('id') for e in root.iter() if e.get('id')]
dupes=[k for k,v in Counter(ids).items() if v>1]
assert not dupes,dupes
counts=Counter(E.QName(e).localname for e in root.iter() if isinstance(e.tag,str))
assert counts['image']==0 and counts['text']==0
assert not any(e.get('filter') for e in root.iter())
out=ROOT/'output';out.mkdir(exist_ok=True)
target=out/'Queen-of-Sidney-rebuilt.svg'
E.ElementTree(root).write(str(target),encoding='UTF-8',xml_declaration=True,pretty_print=True)
qa={'canvas':[1305,1206],'reference_transform':[1,0,0,1,0,0],'comparison_alignment':'identity; original native canvas, no fitted transform or warp','element_counts':dict(counts),'duplicate_ids':dupes,'embedded_images':counts['image'],'live_text':counts['text'],'svg_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
ref=ROOT/'reference'/'original-reference.png'
if not ref.exists(): ref=ROOT.parent/'upload'/'Vintage Queen of Sidney Ferry Sticker(2).png'
if ref.exists(): qa['reference_sha256']=hashlib.sha256(ref.read_bytes()).hexdigest()
(ROOT/'qa'/'vector-validation.json').write_text(json.dumps(qa,indent=2))
print(json.dumps(qa,indent=2))
