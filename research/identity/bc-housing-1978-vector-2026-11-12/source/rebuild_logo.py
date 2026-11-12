"""Manually constructed 1978 BCHMC artwork. No tracing algorithm is used.

The two mark paths use straight segments and deliberate quadratic/cubic joins.
Their anchors were measured from PDF page 3; page 13 clarifies rounded joins.
The name uses fitted Nimbus Sans Bold glyph outlines, supplied separately.
"""
from pathlib import Path
from copy import deepcopy
from xml.etree import ElementTree as ET
import json
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT
OUT.mkdir(parents=True, exist_ok=True)
TMP = ROOT / 'tmp' / 'reconstruction'
TMP.mkdir(parents=True, exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

# Designed paths in reference-crop coordinates, not a sampled pixel contour.
# The first compound path has one genuinely transparent internal counter.
B_PATH = '''M 211.5 39
 C 213.6 39 215.3 39.6 217.6 41
 L 362.8 130.3 Q 368 133.5 368 139.4
 L 368 174.3 Q 368 177.9 364.9 176.1
 L 216.5 88.7 C 209.2 84.4 203 86.9 203 95.7
 L 203 165 C 203 175.7 200.2 180.1 191 186
 C 200.2 192.4 203 196.8 203 207
 L 203 291.3 Q 203 310 184.3 310
 L 64.7 310 Q 46 310 46 291.3
 L 46 150 Q 46 143.2 51.8 139.5
 L 205.4 41.2 C 207.7 39.7 209.3 39 211.5 39 Z
 M 155 124.8 Q 155 120 151 122.4
 L 96.4 155 Q 92 157.6 92 163
 L 92 256.5 Q 92 265 100.5 265
 L 146.5 265 Q 155 265 155 256.5
 L 155 218.5 Q 155 212 148.5 212
 L 111.5 212 Q 104 212 104 204.5
 L 104 186.5 Q 104 179.9 109.6 176.4
 L 150.5 150.8 Q 155 148 155 143 Z'''

C_PATH = '''M 212 119
 C 212 108 216.5 101.8 226 107.5
 L 362.4 188.5 Q 368 191.8 368 198.4
 L 368 207.7 Q 368 212 363.7 212
 L 327.2 212 Q 323 212 323 208.5
 Q 323 205.9 319.4 203.8 L 264 170.8
 Q 258 167.2 258 174
 L 258 256.5 Q 258 265 266.5 265
 L 314.5 265 Q 323 265 323 256.5
 L 323 236.1 Q 323 229 330.1 229
 L 360.9 229 Q 368 229 368 236.1
 L 368 291.3 Q 368 310 349.3 310
 L 230.7 310 Q 212 310 212 291.3 Z'''

COLORS = {'Brown': '#836458', 'Black': '#000000', 'White': '#ffffff'}
WORDMARK = ROOT / 'source' / 'wordmark-outlined.svg'
textroot = ET.parse(WORDMARK).getroot()

def group_symbol(parent):
    g = ET.SubElement(parent, f'{{{NS}}}g', id='house-bc-monogram')
    ET.SubElement(g, f'{{{NS}}}path', id='b-and-outer-roof', d=' '.join(B_PATH.split()), **{'fill-rule': 'evenodd'})
    ET.SubElement(g, f'{{{NS}}}path', id='c-and-inner-roof', d=' '.join(C_PATH.split()))
    return g

def svg_doc(kind='Full_Logo', color='Brown', reference_space=False):
    full = kind == 'Full_Logo'
    scale = 1000 / 322
    width = (1360.168 - 46) * scale if full else 1000
    height = 271 * scale
    pad = 24
    viewbox = f'{-pad} {-pad} {width+pad*2:.5f} {height+pad*2:.5f}'
    size = {'width': f'{width+pad*2:.5f}', 'height': f'{height+pad*2:.5f}'}
    if reference_space:
        viewbox = '0 0 1416 342'
        size = {'width': '1416', 'height': '342'}
    svg = ET.Element(f'{{{NS}}}svg', {'viewBox': viewbox, **size, 'role': 'img', 'aria-labelledby': 'title description'})
    ET.SubElement(svg, f'{{{NS}}}title', id='title').text = f'British Columbia Housing Management Commission, 1978: {"full logo" if full else "BC house symbol"}'
    ET.SubElement(svg, f'{{{NS}}}desc', id='description').text = (
        'A manual vector reconstruction from the supplied 1978 annual report. '
        'The monogram uses two purpose-drawn filled paths with a transparent B counter and roof slit. '
        + ('The three-line name uses outlined Nimbus Sans Bold, optically fitted; the original historical typeface is unverified. ' if full else '')
        + ('Brown is an approximation sampled from the report scan, not a verified official colour specification. ' if color == 'Brown' else '')
        + 'No embedded raster images, live fonts, strokes, filters, or external dependencies. Reconstructed 2026-11-12.'
    )
    artwork = ET.SubElement(svg, f'{{{NS}}}g', id='artwork', fill=COLORS[color])
    if not reference_space:
        artwork.set('transform', f'scale({scale:.12f}) translate(-46 -39)')
    group_symbol(artwork)
    if full:
        word = ET.SubElement(artwork, f'{{{NS}}}g', id='commission-name')
        for g in textroot.findall(f'{{{NS}}}g'):
            n = deepcopy(g)
            n.attrib.pop('fill', None)
            word.append(n)
    ET.indent(svg, space='  ')
    return ET.tostring(svg, encoding='unicode', xml_declaration=True)

for kind in ['Full_Logo', 'Symbol']:
    for color in COLORS:
        (OUT / f'BC_Housing_1978_{kind}_{color}.svg').write_text(svg_doc(kind, color))

# Rendered previews come directly from the authored vector artwork.
for kind, pixels in [('Full_Logo', 3600), ('Symbol', 2000)]:
    path = OUT / f'BC_Housing_1978_{kind}_Brown.svg'
    doc = fitz.open(path)
    doc[0].get_pixmap(matrix=fitz.Matrix(pixels/doc[0].rect.width, pixels/doc[0].rect.width), alpha=True).save(OUT / f'BC_Housing_1978_{kind}_Transparent.png')
    sourcepdf = fitz.open('pdf', doc.convert_to_pdf())
    pdf = fitz.open()
    pagewidth = 720 if kind == 'Full_Logo' else 288
    pageheight = pagewidth * sourcepdf[0].rect.height / sourcepdf[0].rect.width
    page = pdf.new_page(width=pagewidth, height=pageheight)
    page.show_pdf_page(page.rect, sourcepdf, 0)
    pdf.set_metadata({'title': f'BC Housing 1978 - {kind.replace("_", " ")} - Reconstructed vector', 'author': 'Reconstructed from the supplied British Columbia Housing Management Commission 1978 annual report', 'subject': 'Vector reconstruction; original typeface and official ink colour are not verified'})
    pdf.save(OUT / f'BC_Housing_1978_{kind}.pdf', garbage=4, deflate=True)

previewdoc = fitz.open(OUT / 'BC_Housing_1978_Full_Logo_Brown.svg')
previewdoc[0].get_pixmap(matrix=fitz.Matrix(1800/previewdoc[0].rect.width, 1800/previewdoc[0].rect.width), alpha=False).save(OUT / 'BC_Housing_1978_Preview.png')

refsvg = svg_doc('Full_Logo', 'Brown', reference_space=True)
(TMP / 'reference-aligned-rebuild.svg').write_text(refsvg)
rebuild = fitz.open(stream=refsvg.encode(), filetype='svg')
pix = rebuild[0].get_pixmap(alpha=True)
pix.save(TMP / 'reference-aligned-rebuild.png')

ref = Image.open(ROOT / 'source' / 'source-titlepage.png').convert('RGB')
vec = Image.open(TMP / 'reference-aligned-rebuild.png').convert('RGBA')
ra, va = np.array(ref), np.array(vec)
srcmask = (ra[:,:,0]<180) & (ra[:,:,1]<160) & (ra[:,:,2]<155)
vecmask = va[:,:,3]>127
overlay = np.full((*srcmask.shape, 3), 255, dtype=np.uint8)
overlay[srcmask] = [43,146,198]
overlay[vecmask] = [219,78,90]
overlay[srcmask & vecmask] = [53,58,64]
Image.fromarray(overlay).save(TMP / 'alignment-overlay.png')
metrics = {}
for name, cols in [('symbol', slice(0,390)), ('wordmark', slice(400,None)), ('full_logo', slice(None))]:
    sm=srcmask[:,cols]; vm=vecmask[:,cols]
    metrics[name] = {'intersection_over_union': float((sm&vm).sum()/(sm|vm).sum()), 'source_pixels': int(sm.sum()), 'vector_pixels': int(vm.sum())}
(TMP / 'comparison-metrics.json').write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))

font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
regular=ImageFont.truetype(font,23)
small=ImageFont.truetype(font,19)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
proof=Image.new('RGB',(1536,1395),'white')
d=ImageDraw.Draw(proof)
d.text((44,28),'BC HOUSING / 1978',font=bold,fill='#24313b')
d.text((44,76),'British Columbia Housing Management Commission',font=regular,fill='#53616a')
for y,label,im in [(138,'01  ORIGINAL SCAN  /  PDF PAGE 3',ref), (543,'02  REBUILT VECTOR  /  GEOMETRIC SYMBOL + OUTLINED TYPE',vec), (948,'03  ALIGNMENT CHECK  /  SOURCE BLUE, REBUILD RED, SHARED AREA DARK',Image.fromarray(overlay))]:
    d.text((44,y),label,font=small,fill='#53616a')
    # Use the same scale and placement in all rows, without changing image proportions.
    proof.paste(im,(60,y+31),im if im.mode=='RGBA' else None)
d.text((44,1350),'Brown approximates the scan. Typeface is a close reconstruction, not a verified original.',font=small,fill='#53616a')
proof.save(OUT / 'BC_Housing_1978_Comparison.png')
print('Created artwork in', OUT)
