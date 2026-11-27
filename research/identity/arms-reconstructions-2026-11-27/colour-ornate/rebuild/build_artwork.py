"""Rebuild and assemble the source-aligned vector coat of arms."""
from pathlib import Path
import runpy
from lxml import etree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)

# Each component has a self-contained builder and an editable standalone SVG.
for name in ['stag','ram','crest','shield','ribbon']:
    runpy.run_path(str(ROOT/'components'/f'{name}_build.py'),run_name='__main__')

def read_body(name):
    root=ET.parse(str(ROOT/'components'/name)).getroot()
    return ''.join(ET.tostring(c,encoding='unicode') for c in root if ET.QName(c).localname not in ['title','desc','metadata'])

SVG='http://www.w3.org/2000/svg'
INKSCAPE='http://www.inkscape.org/namespaces/inkscape'
body=''.join(read_body(n) for n in ['shield.svg','ribbon.svg','stag.svg','ram.svg','crest.svg'])
doc=f"""<svg xmlns="{SVG}" xmlns:inkscape="{INKSCAPE}" width="1261" height="1247" viewBox="0 0 1261 1247" role="img" aria-labelledby="art-title art-desc">
<title id="art-title">Historical British Columbia coat of arms - revised vector reconstruction</title>
<desc id="art-desc">Reconstructed from the user-supplied ornate historical coat of arms raster. Revised after enlarged comparisons of the antler interiors, scroll curls and seams, shield flag and small crown, sun ray curves, lion paws and crown jewels. Source-guided contours and selectively rebuilt geometry preserve the supplied drawing. Halftone dots and stray pixels are omitted. The motto is outlined: SPLENDOR SINE OCCASU. This is a reconstruction of the supplied drawing, not an authenticated official vector master.</desc>
{body}</svg>"""
root=ET.fromstring(doc.encode())
labels={'shield':'Shield and waves','shield-crown':'Crown on shield','motto-ribbon':'Motto ribbon','motto-lettering':'Outlined motto lettering','stag-supporter':'Stag supporter','ram-supporter':'Ram supporter','lion-crest':'Lion crest','royal-crown':'Royal crown'}
for el in root:
    ident=el.get('id')
    if ident in labels:
        el.set('{'+INKSCAPE+'}groupmode','layer')
        el.set('{'+INKSCAPE+'}label',labels[ident])
dest=OUT/'historical-bc-coat-of-arms.svg'
dest.write_bytes(ET.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True))
print('ASSEMBLED',dest)
