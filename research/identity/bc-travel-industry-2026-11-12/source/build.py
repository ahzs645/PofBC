#!/usr/bin/env python3
"""Assemble the deliberately drawn component SVGs into the finished logo.

Python 3 standard library is sufficient for the SVG. Optional PNG/PDF exports
use Inkscape. No tracing, font conversion, source-image analysis or network
access is performed by this script.

    python source/build.py
    python source/build.py --export

The reference PNG is for the separate comparison only, never the artwork.
"""
from pathlib import Path
from copy import deepcopy
import argparse
import base64
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)


def make_svg():
    root = ET.Element(f'{{{SVG}}}svg', {
        'width': '644', 'height': '468', 'viewBox': '0 0 644 468',
        'version': '1.1', 'role': 'img',
        'aria-labelledby': 'artwork-title artwork-description',
    })
    ET.SubElement(root, f'{{{SVG}}}title', {'id': 'artwork-title'}).text = (
        'British Columbia — Department of Travel Industry')
    ET.SubElement(root, f'{{{SVG}}}desc', {'id': 'artwork-description'}).text = (
        'A hand-reconstructed vector interpretation of the supplied 644 × 468 '
        'pixel logo: a green British Columbia silhouette, two dogwood flowers '
        'and cream lettering. The central flowers were revised to match the additional user-supplied floral reference. Map geometry, floral curves and letterforms were '
        'deliberately rebuilt. No embedded bitmap, automatic tracing, external '
        'font or filter is used. Fine floral details and letterforms are '
        'reconstructed interpretations, not an authenticated original master.')
    labels = {
        'map-shadow': '01 · Black map edge',
        'map-face': '02 · British Columbia silhouette',
        'dogwood-illustration': '03 · Dogwood flowers, leaves and stems',
        'lettering': '04 · Reconstructed lettering',
    }
    for filename in ['map.svg', 'floral.svg', 'lettering.svg']:
        component = ET.parse(HERE / filename).getroot()
        for el in component:
            if el.tag != f'{{{SVG}}}g':
                continue
            layer = deepcopy(el)
            layer.set(f'{{{INK}}}groupmode', 'layer')
            layer.set(f'{{{INK}}}label', labels[layer.get('id')])
            root.append(layer)
    ET.indent(root, space='  ')
    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode') + '\n'
    path = OUT / 'bc_travel_industry_reconstructed.svg'
    path.write_text(content, encoding='utf-8')
    return path, ET.tostring(root, encoding='unicode')


def make_comparison(art):
    reference = OUT / 'reference' / 'this_is_british_columbia_logo.png'
    if not reference.exists():
        return
    ref_uri = 'data:image/png;base64,' + base64.b64encode(reference.read_bytes()).decode()
    svg_uri = 'data:image/svg+xml;base64,' + base64.b64encode(art.encode()).decode()
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>British Columbia logo — reconstruction comparison</title>
<style>
:root{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#1c3025;background:#f4f3ed;font-synthesis:none}
*{box-sizing:border-box}body{margin:0}main{max-width:1440px;margin:auto;padding:32px 28px 44px}
header{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:26px}.kicker{font-size:11px;letter-spacing:.16em;font-weight:750;text-transform:uppercase;color:#4b7059}h1{font-size:clamp(24px,3.6vw,38px);font-weight:650;letter-spacing:-.04em;margin:8px 0 9px;line-height:1.12}p{margin:0;max-width:850px;color:#506158;font-size:14px;line-height:1.6}
a.download{border:1px solid #1c4730;padding:11px 18px;border-radius:7px;background:#1c4730;color:white;text-decoration:none;white-space:nowrap;font-size:13px;font-weight:600}
.toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:18px;margin-bottom:16px}.modes{display:flex;gap:4px;background:#e7e9e0;padding:4px;border-radius:8px}button{font:inherit;font-size:13px;border:0;border-radius:5px;background:transparent;padding:9px 14px;color:#506158;cursor:pointer}button.active{background:#fff;color:#183d29;box-shadow:0 1px 3px #0001}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #8fa786;outline-offset:3px}
.slider{display:flex;align-items:center;gap:12px;font-size:13px}.slider input{width:160px;accent-color:#316746}output{font-variant-numeric:tabular-nums;min-width:38px}.layers{margin-left:auto;display:flex;gap:13px;flex-wrap:wrap}.layers label{font-size:12px;cursor:pointer;display:flex;align-items:center;gap:5px}.layers input{accent-color:#316746}.disabled{opacity:.4;pointer-events:none}
.side{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{background:white;border:1px solid #dcdfd5;border-radius:10px;overflow:hidden}.label{font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;padding:15px 18px 11px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;gap:10px}.label span{font-weight:400;letter-spacing:0;text-transform:none;color:#6e7a71}.image{padding:18px;line-height:0}.image>img,.image>svg{display:block;width:100%;height:auto}.single{max-width:980px;margin:0 auto}.stack{position:relative;aspect-ratio:644/468;background:white;overflow:hidden}.stack>img,.stack>div{position:absolute;inset:0;width:100%;height:100%}.stack svg{display:block;width:100%;height:100%}.divider{position:absolute!important;width:2px!important;height:100%;background:#b16c34;left:50%;pointer-events:none;box-shadow:0 0 0 1px #fff9}.footnote{display:flex;justify-content:space-between;gap:20px;margin-top:16px;font-size:12px;line-height:1.55;color:#6b756d}.footnote p{font-size:12px;max-width:850px}.hidden{display:none!important}.checker{background:repeating-conic-gradient(#e9ece6 0% 25%,#fff 0% 50%) 50% / 18px 18px}
@media(max-width:760px){main{padding:22px 14px}header{align-items:flex-start;flex-direction:column;gap:15px}.side{grid-template-columns:1fr}.layers{margin-left:0;width:100%}.toolbar{gap:12px}.modes{overflow:auto;max-width:100%}button{padding:8px 10px;font-size:12px}.slider input{width:130px}.image{padding:10px}.footnote{display:block}.footnote p+p{margin-top:8px}}
</style></head><body><main>
<header><div><div class="kicker">Vector reconstruction · reference review</div><h1>British Columbia<br>Department of Travel Industry</h1><p>Compare the supplied image with the remade artwork. The central flowers now follow the additional floral reference below; the original map and lettering are retained.</p></div><a class="download" href="__SVG_URI__" download="bc_travel_industry_reconstructed.svg">Download SVG</a></header>
<div class="toolbar"><div class="modes" role="group" aria-label="Comparison mode"><button class="active" data-mode="side" aria-pressed="true">Side by side</button><button data-mode="wipe" aria-pressed="false">Wipe</button><button data-mode="overlay" aria-pressed="false">Overlay</button><button data-mode="vector" aria-pressed="false">Vector only</button></div><label class="slider hidden" id="slider-wrap"><span id="slider-label">Vector opacity</span><input id="slider" type="range" min="0" max="100" value="50" aria-label="Vector opacity"><output id="amount" for="slider">50%</output></label><div class="layers" id="layers"><label><input type="checkbox" data-layer="map-face,map-shadow" checked>Map</label><label><input type="checkbox" data-layer="dogwood-illustration" checked>Dogwood</label><label><input type="checkbox" data-layer="lettering" checked>Lettering</label></div></div>
<section class="side" id="side"><div class="panel"><div class="label">Supplied reference<span>644 × 468 pixels</span></div><div class="image"><img src="__REF_URI__" alt="Supplied raster logo reference"></div></div><div class="panel"><div class="label">Reconstructed vector<span>Independent editable shapes</span></div><div class="image vector-art" id="side-vector">__ART__</div></div></section>
<section class="single panel hidden" id="single"><div class="label"><span id="view-label">Overlay comparison</span><span id="view-hint">Reference below · vector above</span></div><div class="image"><div class="stack" id="stack"><img id="reference" src="__REF_URI__" alt="Supplied reference beneath the vector"><div class="vector-art" id="compare-vector">__ART_COMPARE__</div><div class="divider hidden" id="divider"></div></div></div></section>
__DETAIL_SECTION__<div class="footnote"><p>The overall comparison uses the first supplied logo. The central flowers have been revised to the additional floral reference shown below. Lettering remains reconstructed; scan grain and colour fringing are intentionally removed.</p><p>SVG: no bitmap, font or external dependency.<br>Transparent background in the downloaded artwork.</p></div>
</main><script>
const $=s=>document.querySelector(s);let mode='side';const slider=$('#slider');
function paint(){const v=Number(slider.value);$('#amount').value=v+'%';const a=$('#compare-vector');a.style.opacity=mode==='overlay'?v/100:1;a.style.clipPath=mode==='wipe'?'inset(0 '+(100-v)+'% 0 0)':'none';$('#divider').style.left=v+'%';}
function setMode(next){mode=next;document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode)});$('#side').classList.toggle('hidden',mode!=='side');$('#single').classList.toggle('hidden',mode==='side');$('#slider-wrap').classList.toggle('hidden',!['wipe','overlay'].includes(mode));$('#reference').classList.toggle('hidden',mode==='vector');$('#divider').classList.toggle('hidden',mode!=='wipe');$('#stack').classList.toggle('checker',mode==='vector');$('#view-label').textContent=({wipe:'Wipe comparison',overlay:'Overlay comparison',vector:'Reconstructed vector'})[mode]||'';$('#view-hint').textContent=mode==='vector'?'Transparent background':mode==='wipe'?'Vector at left · reference at right':'Reference below · vector above';$('#slider-label').textContent=mode==='wipe'?'Reveal vector':'Vector opacity';slider.setAttribute('aria-label',mode==='wipe'?'Reveal vector':'Vector opacity');paint();}
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));slider.addEventListener('input',paint);
document.querySelectorAll('[data-layer]').forEach(c=>c.addEventListener('change',()=>{for(const id of c.dataset.layer.split(',')){document.querySelectorAll('.vector-art [data-original-id="'+id+'"]').forEach(g=>g.style.display=c.checked?'':'none');}}));paint();
</script></body></html>'''
    # Inline copies use unique IDs to prevent document-level collisions.
    def embedded_svg(prefix):
        root = ET.fromstring(art)
        for el in root.iter():
            if el.get('id'):
                old = el.get('id')
                el.set('data-original-id', old)
                el.set('id', prefix + old)
            if el.get('aria-labelledby'):
                el.set('aria-labelledby', ' '.join(prefix + p for p in el.get('aria-labelledby').split()))
        return ET.tostring(root, encoding='unicode')
    page = page.replace('__REF_URI__', ref_uri).replace('__SVG_URI__', svg_uri)
    page = page.replace('__ART__', embedded_svg('side-')).replace('__ART_COMPARE__', embedded_svg('compare-'))
    detail_reference = OUT / 'reference' / 'floral_detail_reference.png'
    if detail_reference.exists():
        detail_uri = 'data:image/png;base64,' + base64.b64encode(detail_reference.read_bytes()).decode()
        detail_root = ET.fromstring(art)
        detail_root.set('viewBox', '191.875758 160.110094 282.834662 169.212098')
        detail_root.set('width', '463')
        detail_root.set('height', '277')
        detail_svg_uri = 'data:image/svg+xml;base64,' + base64.b64encode(ET.tostring(detail_root)).decode()
        detail = '<h2 style="font-size:21px;margin:32px 0 14px">Revised central illustration</h2><section class="side"><div class="panel"><div class="label">New floral reference<span>Supplied detail</span></div><div class="image"><img src="' + detail_uri + '" alt="New floral detail supplied by the user"></div></div><div class="panel"><div class="label">Rebuilt centre<span>New editable vector shapes</span></div><div class="image"><img src="' + detail_svg_uri + '" alt="Reconstructed central dogwood illustration"></div></div></section>'
    else:
        detail = ''
    page = page.replace('__DETAIL_SECTION__', detail)
    (OUT / 'bc_travel_industry_comparison.html').write_text(page, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='Also export PNG and PDF using Inkscape')
    args = parser.parse_args()
    path, art = make_svg()
    make_comparison(art)
    if args.export:
        subprocess.run(['inkscape', str(path), '--export-width=2576',
                        '--export-filename=' + str(OUT / 'bc_travel_industry_transparent.png')], check=True)
        subprocess.run(['inkscape', str(path), '--export-type=pdf',
                        '--export-filename=' + str(OUT / 'bc_travel_industry_vector.pdf')], check=True)
    print(path)


if __name__ == '__main__':
    main()
