#!/usr/bin/env python3
"""Rebuild the 1971 Forest Service ad from placed assets and real font outlines.

Requirements: Python 3, Pillow with RAQM, fontTools, reportlab, Inkscape, Poppler.
Run in any directory: python3 /path/to/build_ad.py
The photograph is embedded unchanged. No raster tracing is used.
"""
from pathlib import Path
from base64 import b64encode
from copy import deepcopy
import html
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

from PIL import Image, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLFont

ROOT = Path(__file__).resolve().parent
W, H = 565, 1044
PAPER, INK = '#E9CDAD', '#3D372F'
SIZE, Y_SCALE, SHEAR = 34.0, 0.96, 0.04
SOURCE = 'https://saltspringarchives.com/driftwood/1971/v12n47Dec2-1971.pdf#page=11'
FONT_PATH = ROOT / 'fonts/ForestAdSans-SemiBoldItalic.ttf'
FT = TTFont(FONT_PATH)
GLYPHS = FT.getGlyphSet()
CMAP = FT.getBestCmap()
UPEM = FT['head'].unitsPerEm
MEASURE = ImageFont.truetype(str(FONT_PATH), 1000)
FEATURES = ['-liga', '-calt']

LINES = [
    {'id':'headline-1', 'text':'With proper management', 'x':81, 'y':745, 'width':409},
    {'id':'headline-2', 'text':'British Columbia’s forests', 'x':81, 'y':782, 'width':404},
    {'id':'headline-3', 'text':'will last a coon’s age.', 'x':81, 'y':818, 'width':351},
    {'id':'signature-1', 'text':'British Columbia', 'x':214, 'y':911, 'width':259},
    {'id':'signature-2', 'text':'Forest Service', 'x':239, 'y':948, 'width':214},
]

def uri(path, mime):
    return f'data:{mime};base64,' + b64encode(Path(path).read_bytes()).decode('ascii')

def path_and_bounds(text, tracking):
    out = SVGPathPen(GLYPHS)
    bounds = BoundsPen(GLYPHS)
    scale = SIZE / UPEM
    for i, ch in enumerate(text):
        # Prefix widths include the preceding pair's kerning. Ligatures are disabled.
        advance = (MEASURE.getlength(text[:i+1], features=FEATURES)
                   - MEASURE.getlength(ch, features=FEATURES)) * SIZE / 1000
        advance += i * tracking
        transform = (scale, 0, -scale*SHEAR, -scale*Y_SCALE, advance, 0)
        glyph = GLYPHS[CMAP[ord(ch)]]
        glyph.draw(TransformPen(out, transform))
        glyph.draw(TransformPen(bounds, transform))
    return out.getCommands(), bounds.bounds

def fit_line(line):
    tracking = 0.0
    for _ in range(4):
        d, b = path_and_bounds(line['text'], tracking)
        tracking += (line['width'] - (b[2]-b[0])) / (len(line['text'])-1)
    d, b = path_and_bounds(line['text'], tracking)
    return dict(line, tracking=round(tracking, 6), origin=round(line['x']-b[0],6),
                bounds=[round(v,4) for v in b], path=d)

FITTED = [fit_line(line) for line in LINES]

def emblem_markup():
    root = ET.parse(ROOT/'assets/forest-service-emblem-newspaper.svg').getroot()
    for el in root.iter():
        if 'id' in el.attrib:
            el.set('id', 'ad-emblem-' + el.get('id'))
        for attr in ('fill','stroke'):
            value = el.get(attr,'').lower()
            if value == '#111111': el.set(attr, INK)
            if value == '#ffffff': el.set(attr, PAPER)
    root.set('x','92')
    root.set('y','867')
    root.set('width','114')
    root.set('height','121')
    root.set('preserveAspectRatio','xMidYMid meet')
    root.set('aria-label','PofBC Forest Service emblem, newspaper paint treatment')
    root.attrib.pop('aria-labelledby',None)
    return ET.tostring(root, encoding='unicode')

def svg_document(outlined=False):
    font_css = '' if outlined else (
        '<style>@font-face{font-family:"Forest Ad Sans";font-weight:600;'
        'font-style:italic;src:url("' + uri(ROOT/'fonts/ForestAdSans-SemiBoldItalic.woff','font/woff')
        + '") format("woff");}text{font-family:"Forest Ad Sans";font-weight:600;'
        'font-style:italic;font-kerning:normal;font-variant-ligatures:none;}</style>'
    )
    contents = []
    for line in FITTED:
        if outlined:
            content = (f'<g id="{line["id"]}" role="img" aria-label="{html.escape(line["text"])}" '
                       f'transform="translate({line["origin"]} {line["y"]})">'
                       f'<path d="{line["path"]}"/></g>')
        else:
            content = (f'<g id="{line["id"]}" transform="translate({line["origin"]} {line["y"]}) '
                       f'matrix(1 0 {SHEAR} {Y_SCALE} 0 0)">'
                       f'<text x="0" y="0" font-size="{SIZE}" '
                       f'letter-spacing="{line["tracking"]}" xml:space="preserve">'
                       f'{html.escape(line["text"])}</text></g>')
        contents.append(content)
    photo_height = 452 * 1513 / 1040
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
 width="100mm" height="{100*H/W:.6f}mm" viewBox="0 0 {W} {H}" role="img"
 aria-labelledby="art-title art-desc">
<title id="art-title">British Columbia Forest Service raccoon advertisement — reconstruction</title>
<desc id="art-desc">Reconstructed from Gulf Islands Driftwood, 2 December 1971, page 11.
Supplied photograph placed unchanged, PofBC emblem geometry retained with newspaper paint treatment,
editable font-based lettering or matching glyph outlines. Likely Futura-family oblique in the original;
this reconstruction uses a named static derivative of Jost Italic weight 600, not an authenticated original font.</desc>
<metadata>Source: {html.escape(SOURCE)}; working artboard 565 x 1044; export width 100 mm;
PofBC source revision 00cf5d68d7574897a52414f8b0744c1a4c0e508d.
Font vertical scale {Y_SCALE}; reduced italic shear {SHEAR}; line-specific tracking fitted to scan.</metadata>
{font_css}
<g inkscape:groupmode="layer" inkscape:label="01 Paper and border" id="paper-border">
 <rect width="565" height="1044" fill="{PAPER}"/>
 <rect x="6" y="3" width="553" height="1036" fill="none" stroke="{INK}" stroke-width="4"/>
</g>
<g inkscape:groupmode="layer" inkscape:label="02 Supplied photograph" id="photograph">
 <image x="60" y="17" width="452" height="{photo_height:.8f}" preserveAspectRatio="xMidYMid meet"
 xlink:href="{uri(ROOT/'assets/raccoon-supplied.png','image/png')}"/>
</g>
<g inkscape:groupmode="layer" inkscape:label="03 Ink panels" id="ink-panels" fill="{INK}">
 <rect x="75" y="714" width="420" height="116"/>
 <rect x="94" y="870" width="401" height="115"/>
</g>
<g inkscape:groupmode="layer" inkscape:label="04 Forest Service emblem" id="forest-service-emblem">
{emblem_markup()}
</g>
<g inkscape:groupmode="layer" inkscape:label="05 {'Outlined' if outlined else 'Editable'} lettering" id="lettering" fill="{PAPER}">
{''.join(contents)}
</g>
</svg>
'''

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def render_artwork():
    editable = ROOT/'Forest_Service_Raccoon_Ad_Editable.svg'
    outlined = ROOT/'Forest_Service_Raccoon_Ad_Outlined.svg'
    editable.write_text(svg_document(False),encoding='utf-8')
    outlined.write_text(svg_document(True),encoding='utf-8')
    run('inkscape',str(outlined),'--export-type=png',
        '--export-filename='+str(ROOT/'Forest_Service_Raccoon_Ad.png'),'--export-width=1130')
    run('inkscape',str(outlined),'--export-type=pdf',
        '--export-filename='+str(ROOT/'Forest_Service_Raccoon_Ad.pdf'))
    (ROOT/'reference/fitted-layout.json').write_text(json.dumps({
        'working_artboard':[W,H], 'export_width_mm':100,
        'paper':PAPER,'ink':INK,'font_size':SIZE,'vertical_scale':Y_SCALE,
        'shear_adjustment':SHEAR,
        'lines':[{k:v for k,v in l.items() if k!='path'} for l in FITTED]
    },indent=2,ensure_ascii=False),encoding='utf-8')

def proof_pdf():
    path = ROOT/'Forest_Service_Raccoon_Comparison.pdf'
    c = canvas.Canvas(str(path), pagesize=(960,910))
    c.setTitle('Forest Service raccoon ad — source and reconstruction')
    regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    pdfmetrics.registerFont(RLFont('ProofSans',regular))
    pdfmetrics.registerFont(RLFont('ProofSansBold',bold))
    c.setFillColor(HexColor('#F7F5F0'));c.rect(0,0,960,910,fill=1,stroke=0)
    c.setFillColor(HexColor('#192A35'));c.setFont('ProofSansBold',23)
    c.drawString(40,863,'British Columbia Forest Service')
    c.setFont('ProofSans',12);c.setFillColor(HexColor('#58646B'))
    c.drawString(40,839,'Raccoon advertisement / 2 December 1971 / source and reconstruction')
    width=365; height=width*H/W
    for x, label, file in [(42,'ORIGINAL NEWSPAPER SCAN',ROOT/'reference/original-ad-1971-12-02.png'),
                            (553,'REBUILT ARTWORK',ROOT/'Forest_Service_Raccoon_Ad.png')]:
        c.setFont('ProofSansBold',10);c.setFillColor(HexColor('#293F4D'))
        c.drawString(x,807,label)
        c.drawImage(ImageReader(str(file)),x,116,width=width,height=height,mask='auto')
    c.setStrokeColor(HexColor('#D1D4D1'));c.line(40,96,920,96)
    c.setFillColor(HexColor('#334650'));c.setFont('ProofSans',10)
    c.drawString(40,76,'Rebuilt with the supplied photograph, real font lettering, geometric panels, and existing PofBC emblem paths.')
    c.drawString(40,59,'Typeface: likely Futura-family oblique in the scan; Jost Italic 600 is a disclosed modern substitute.')
    c.drawString(40,42,'The emblem keeps the selected master geometry. Its tree and coastline differ slightly from this newspaper impression.')
    c.setFont('ProofSans',8);c.setFillColor(HexColor('#657279'))
    c.drawString(40,23,'Source: Gulf Islands Driftwood, 2 December 1971, printed p. 11. Paper tone, size and spacing are reconstructed from the scan.')
    c.linkURL(SOURCE,(40,16,920,34),relative=0,thickness=0)
    c.save()
    run('pdftoppm','-f','1','-singlefile','-scale-to','1500','-png',str(path),
        str(ROOT/'Forest_Service_Raccoon_Comparison'))

def review_html():
    original=uri(ROOT/'reference/original-ad-1971-12-02.png','image/png')
    recreated=uri(ROOT/'Forest_Service_Raccoon_Ad_Outlined.svg','image/svg+xml')
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Forest Service raccoon ad — comparison</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f3ee;color:#182e3d;font:16px/1.55 system-ui,sans-serif}
main{max-width:1160px;padding:30px 24px 60px;margin:auto}h1{font-size:clamp(25px,4vw,40px);letter-spacing:-.03em;margin:0 0 8px}
.intro{max-width:780px;color:#4e606b;margin:0 0 22px}.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:18px 0}
button{background:white;border:1px solid #bdc9cc;border-radius:7px;padding:9px 14px;color:#18384a;font:inherit;cursor:pointer}
button[aria-pressed=true]{background:#18384a;color:white;border-color:#18384a}input{accent-color:#18384a;width:180px}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:26px}.panel h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin:0 0 10px}
.panel img{width:100%;height:auto;display:block;box-shadow:0 4px 18px #142f3d15}
.overlay{position:relative;width:min(565px,100%);margin:auto}.overlay img{display:block;width:100%}.overlay .rebuilt{position:absolute;inset:0;opacity:.5}
.hidden{display:none!important}.notes{margin:30px 0 0;border-top:1px solid #cdd4d3;padding-top:22px;display:grid;grid-template-columns:1fr 1fr;gap:24px}
.notes h2{font-size:18px;margin:0 0 8px}.notes p{margin:0 0 10px;color:#455a65}a{color:#165c87}code{font-size:.9em;background:#e9ece8;padding:1px 4px}
@media(max-width:650px){main{padding:20px 16px}.compare,.notes{grid-template-columns:1fr}.compare{gap:25px}.toolbar{gap:8px}.toolbar label{width:100%}}
@media print{.toolbar{display:none}.notes{font-size:11px}.compare{grid-template-columns:1fr 1fr}.panel img{box-shadow:none}body{background:white}}
</style><main><h1>Forest Service raccoon advertisement</h1>
<p class="intro">An editable reconstruction of the ad in <em>Gulf Islands Driftwood</em>, 2 December 1971, page 11. Compare the source with the rebuilt photograph, lettering, panels and emblem.</p>
<div class="toolbar" aria-label="Comparison mode"><button id="side" aria-pressed="true">Side by side</button><button id="over" aria-pressed="false">Overlay</button><label id="blend-label" class="hidden" for="blend">Reconstruction opacity <input id="blend" type="range" min="0" max="100" value="50"><output id="value">50%</output></label></div>
<section class="compare" id="side-view"><div class="panel"><h2>Original newspaper scan</h2><img id="original-source" src="__ORIGINAL__" alt="Original 1971 newspaper advertisement"></div><div class="panel"><h2>Reconstructed artwork</h2><img id="reconstruction-source" src="__RECREATED__" alt="Recreated advertisement with supplied raccoon image and font lettering"></div></section>
<section id="overlay-view" class="overlay hidden" aria-label="Original and reconstruction overlay"><img id="overlay-original" alt="Original advertisement"><img id="overlay-image" class="rebuilt" alt="Reconstruction overlay"></section>
<section class="notes"><div><h2>Typography</h2><p>The scan suggests a Futura-family oblique: geometric bowls, single-storey <strong>a</strong> and <strong>g</strong>, and sloping sans serif capitals. The exact historical cut is unconfirmed.</p><p>This version uses <strong>Jost Italic, weight 600</strong>, packaged as Forest Ad Sans. Tracking is fitted by line, the vertical scale is 96%, and the slant is slightly reduced. All letters originate from font outlines.</p></div><div><h2>Artwork and editing</h2><p>The supplied photograph is embedded without retouching or cropping. The selected PofBC emblem retains its existing paths, with the outlined mainland, light tree and dark badge treatment seen in the ad.</p><p>Use the editable SVG with the supplied TTF for text changes. Use the outlined SVG or PDF for a stable, font-independent result. The square emblem is placed proportionally, so a few differences from the aged print remain.</p></div></section>
<p><a href="__SOURCE__">Open the original newspaper, page 11</a> · <a href="https://projects.ahmadjalil.com/PofBC/?view=internal&amp;internal=forests&amp;internal-logo=forest-service-emblem">PofBC emblem</a></p>
</main><script>
document.getElementById('overlay-original').src=document.getElementById('original-source').src;document.getElementById('overlay-image').src=document.getElementById('reconstruction-source').src;
const side=document.getElementById('side'),over=document.getElementById('over'),sideView=document.getElementById('side-view'),overlayView=document.getElementById('overlay-view'),blendLabel=document.getElementById('blend-label');
function mode(overlay){side.setAttribute('aria-pressed',String(!overlay));over.setAttribute('aria-pressed',String(overlay));sideView.classList.toggle('hidden',overlay);overlayView.classList.toggle('hidden',!overlay);blendLabel.classList.toggle('hidden',!overlay)}
side.addEventListener('click',()=>mode(false));over.addEventListener('click',()=>mode(true));
document.getElementById('blend').addEventListener('input',e=>{document.getElementById('overlay-image').style.opacity=e.target.value/100;document.getElementById('value').textContent=e.target.value+'%'});
</script></html>'''
    (ROOT/'Forest_Service_Raccoon_Review.html').write_text(content.replace('__ORIGINAL__',original).replace('__RECREATED__',recreated).replace('__SOURCE__',SOURCE),encoding='utf-8')

if __name__ == '__main__':
    render_artwork()
    proof_pdf()
    review_html()
    print(json.dumps({'created':['Forest_Service_Raccoon_Ad_Editable.svg','Forest_Service_Raccoon_Ad_Outlined.svg','Forest_Service_Raccoon_Ad.pdf','Forest_Service_Raccoon_Ad.png','Forest_Service_Raccoon_Comparison.pdf','Forest_Service_Raccoon_Review.html'],'fitted_lines':[{k:v for k,v in l.items() if k!='path'} for l in FITTED]},indent=2,ensure_ascii=False))
