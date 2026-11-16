#!/usr/bin/env python3
"""Compare BC Trade flag revisions at the scan's fixed four-to-one registration.

Usage, from the repository root:
    python3 research/identity/bc-trade-vector-2026-11-13/source/overlay_bc_trade.py \
        --before /path/to/previous-bc-trade.svg

The current public master and the unmodified 196 x 218 scan are read from this
repository. No fitting, edge tracing, rotation or warping is applied. Visible
colour boundaries come from flattened Inkscape renders: covered construction
paths, clipping boundaries and invisible white-on-white edges are excluded.

Requires Python 3, Pillow, numpy, scipy, and Inkscape on PATH. Writes only the
two review deliverables beside this source folder. Render intermediates live in
a temporary directory. The HTML embeds every image and works without a server.
"""

import argparse
import base64
import hashlib
import html
import io
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


PACKAGE = Path(__file__).resolve().parent.parent
REPO = PACKAGE.parents[2]
MASTER = REPO / "public/identity-collected/bc-trade/bc-trade-1991-rebuilt.svg"
SCAN = REPO / "public/identity-collected/bc-trade/bc-trade-1991-scan.png"
ARTBOARD = (784, 872)
RENDER_SCALE = 3
FLAG_CROP = (62, 392, 690, 746)
MAGENTA = (203, 35, 157)
CYAN = (0, 156, 185)
PAPER = "#F5F4EF"
INK = "#172D48"
MUTED = "#53616A"
LINE = "#D8DEDE"
POINTS = [
    {"number": 1, "name": "Upper central blue tip", "x": 593, "y": 467, "size": [144, 96], "badge": [640, 407]},
    {"number": 2, "name": "Lower-right blue tip", "x": 537, "y": 608, "size": [144, 96], "badge": [614, 676]},
    {"number": 3, "name": "Left blue wedge", "x": 226, "y": 587, "size": [128, 92], "badge": [137, 588]},
    {"number": 4, "name": "First flag fold", "x": 286, "y": 493, "size": [128, 100], "badge": [303, 414]},
    {"number": 5, "name": "Second flag fold", "x": 518, "y": 471, "size": [128, 100], "badge": [508, 404]},
    {"number": 6, "name": "Upper-left red cap", "x": 250, "y": 604, "size": [116, 96], "badge": [197, 661]},
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_artboard(file):
    root = ET.parse(file).getroot()
    box = [float(n) for n in root.attrib.get("viewBox", "").replace(",", " ").split()]
    if box != [0, 0, *ARTBOARD]:
        raise ValueError(f"{file}: expected unchanged viewBox='0 0 784 872'; refusing to fit it")


def render(file, destination):
    process = subprocess.run([
        "inkscape", str(file), "--export-area-page",
        f"--export-width={ARTBOARD[0] * RENDER_SCALE}",
        f"--export-filename={destination}",
    ], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "Inkscape failed")
    image = Image.open(destination).convert("RGBA")
    expected = tuple(v * RENDER_SCALE for v in ARTBOARD)
    if image.size != expected:
        raise ValueError(f"Unexpected render size {image.size}; expected {expected}")
    return image


def visible_outline(rendered, colour):
    """Thin boundaries between colours in the final flattened image, not paths.

    Quantization assigns antialiased pixels to the nearest published flat colour.
    White paint and transparent pixels are both white on the review's white ground,
    so an invisible outer white boundary cannot become a misleading contour.
    """
    rgba = np.asarray(rendered, dtype=np.float32)
    alpha = rgba[..., 3:4] / 255
    flattened = rgba[..., :3] * alpha + 255 * (1 - alpha)
    palette = np.array([[255, 255, 255], [178, 44, 32], [23, 68, 127],
                        [237, 196, 69], [17, 17, 17]], dtype=np.float32)
    nearest = np.full(flattened.shape[:2], np.inf, dtype=np.float32)
    labels = np.zeros(flattened.shape[:2], dtype=np.uint8)
    for index, value in enumerate(palette):
        distance = ((flattened - value) ** 2).sum(axis=2)
        closer = distance < nearest
        labels[closer] = index
        nearest[closer] = distance[closer]
    edge = np.zeros(labels.shape, dtype=bool)
    edge[1:, :] |= labels[1:, :] != labels[:-1, :]
    edge[:, 1:] |= labels[:, 1:] != labels[:, :-1]
    # About one SVG unit wide after downsampling: thin, but visible on the scan.
    ink = ndimage.distance_transform_edt(~edge) <= 1.15
    output = np.zeros((*edge.shape, 4), dtype=np.uint8)
    output[..., :3] = colour
    output[..., 3] = ink.astype(np.uint8) * 255
    return Image.fromarray(output, "RGBA")


def registered_crop(image, crop, width, is_scan=False):
    x0, y0, x1, y1 = crop
    height = round(width * (y1 - y0) / (x1 - x0))
    if is_scan:
        # Retain the original pixels visibly. Enlargement adds no source detail.
        full = image.resize(tuple(v * RENDER_SCALE for v in ARTBOARD), Image.Resampling.NEAREST)
    else:
        full = image
    box = tuple(round(v * RENDER_SCALE) for v in crop)
    return full.crop(box).resize((width, height), Image.Resampling.NEAREST if is_scan else Image.Resampling.LANCZOS)


def overlaid(scan, before_edge, after_edge, crop, width, opacity=225):
    base = registered_crop(scan, crop, width, True).convert("RGBA")
    for boundary in (before_edge, after_edge):
        layer = registered_crop(boundary, crop, width)
        layer.putalpha(layer.getchannel("A").point(lambda value: value * opacity // 255))
        base = Image.alpha_composite(base, layer)
    return base.convert("RGB")


def font(size, bold=False):
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def paragraph(draw, text, xy, width, size=21, colour=MUTED, spacing=8):
    x, y = xy
    face = font(size)
    for block in text.split("\n"):
        words = block.split()
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if line and draw.textlength(candidate, font=face) > width:
                draw.text((x, y), line, font=face, fill=colour)
                y += size + spacing
                line = word
            else:
                line = candidate
        if line:
            draw.text((x, y), line, font=face, fill=colour)
            y += size + spacing
    return y


def paste_card(canvas, image, xy, title, subtitle, width):
    x, y = xy
    draw = ImageDraw.Draw(canvas)
    draw.text((x, y), title, font=font(25, True), fill=INK)
    draw.text((x, y + 37), subtitle, font=font(17), fill=MUTED)
    box_y = y + 72
    flat = Image.new("RGBA", image.size, "white")
    flat.alpha_composite(image.convert("RGBA"))
    canvas.paste(flat.convert("RGB"), (x, box_y))
    draw.rectangle((x, box_y, x + width - 1, box_y + image.height - 1), outline=LINE, width=1)


def annotate(draw, origin, crop, scale, points=POINTS):
    ox, oy = origin
    for point in points:
        px = ox + (point["x"] - crop[0]) * scale
        py = oy + (point["y"] - crop[1]) * scale
        bx = ox + (point["badge"][0] - crop[0]) * scale
        by = oy + (point["badge"][1] - crop[1]) * scale
        draw.line((px, py, bx, by), fill=INK, width=2)
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=PAPER, outline=INK, width=2)
        draw.ellipse((bx - 17, by - 17, bx + 17, by + 17), fill=INK)
        label = str(point["number"])
        box = draw.textbbox((0, 0), label, font=font(19, True))
        draw.text((bx - (box[2] - box[0]) / 2, by - 14), label, font=font(19, True), fill="white")


def static_sheet(scan, before, after, before_edge, after_edge, hashes):
    canvas = Image.new("RGB", (1840, 2188), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((48, 34), "POFBC  /  REGISTERED REFERENCE REVIEW", font=font(18, True), fill=MUTED)
    draw.text((48, 72), "BC Trade / flag geometry", font=font(52, True), fill=INK)
    draw.text((48, 143), "Original scan + visible vector boundaries. One fixed registration; no separate fitting or warping.", font=font(23), fill=MUTED)

    card_width = 560
    for x, title, subtitle, image in [
        (48, "Reference scan", "Original 196 x 218 pixels; enlarged flag crop", registered_crop(scan, FLAG_CROP, card_width, True)),
        (640, "Before correction", "Previous vector / " + hashes["before"][:12], registered_crop(before, FLAG_CROP, card_width)),
        (1232, "After correction", "Corrected vector / " + hashes["after"][:12], registered_crop(after, FLAG_CROP, card_width)),
    ]:
        paste_card(canvas, image, (x, 210), title, subtitle, card_width)

    draw.text((48, 648), "TRUE SUPERIMPOSITION", font=font(20, True), fill=INK)
    draw.line((430, 662, 477, 662), fill=MAGENTA, width=3)
    draw.text((490, 647), "Before", font=font(20), fill=INK)
    draw.line((625, 662, 672, 662), fill=CYAN, width=3)
    draw.text((685, 647), "After", font=font(20), fill=INK)
    overlay_width = 1138
    main_overlay = overlaid(scan, before_edge, after_edge, FLAG_CROP, overlay_width)
    canvas.paste(main_overlay, (48, 698))
    draw.rectangle((48, 698, 48 + overlay_width - 1, 698 + main_overlay.height - 1), outline=LINE)
    annotate(draw, (48, 698), FLAG_CROP, overlay_width / (FLAG_CROP[2] - FLAG_CROP[0]))

    info_x, info_width = 1232, 560
    draw.text((info_x, 698), "Read the overlay", font=font(27, True), fill=INK)
    y = paragraph(draw, "Magenta = before. Cyan = after. These are thin outlines of final visible colour boundaries over the same original pixels.", (info_x, 746), info_width)
    y = paragraph(draw, "Matching contours can overlap. The offline viewer lets you show either revision alone and change opacity.", (info_x, y + 14), info_width)
    draw.text((info_x, y + 22), "Fixed registration", font=font(24, True), fill=INK)
    y = paragraph(draw, "1 scan pixel = 4 SVG units. Both vectors retain the 784 x 872 artboard. The main overlay displays the scan at about 7.2x its native size.", (info_x, y + 62), info_width)
    draw.text((info_x, y + 22), "What remains uncertain", font=font(24, True), fill=INK)
    paragraph(draw, "The scan is small and already blurred. Soft pixels do not prove that every original corner was rounded. The numbered anchors locate inspection areas; they are not measurements of a recovered original vector.", (info_x, y + 62), info_width)

    draw.text((48, 1394), "SIX INSPECTION AREAS", font=font(20, True), fill=INK)
    draw.text((48, 1430), "The same registered overlay, enlarged further. Original pixels are intentionally visible.", font=font(21), fill=MUTED)
    for index, point in enumerate(POINTS):
        column, row = index % 3, index // 3
        x, y = 48 + column * 592, 1490 + row * 296
        draw.rounded_rectangle((x, y, x + 560, y + 270), radius=10, fill="white", outline=LINE)
        draw.text((x + 18, y + 14), f'{point["number"]}  {point["name"]}', font=font(21, True), fill=INK)
        draw.text((x + 18, y + 47), f'Anchor ({point["x"]}, {point["y"]}) in the unchanged SVG artboard', font=font(16), fill=MUTED)
        cw, ch = point["size"]
        crop = (point["x"] - cw / 2, point["y"] - ch / 2, point["x"] + cw / 2, point["y"] + ch / 2)
        tile_width = min(510, round(177 * cw / ch))
        tile = overlaid(scan, before_edge, after_edge, crop, tile_width)
        tx, ty = x + (560 - tile_width) // 2, y + 81
        canvas.paste(tile, (tx, ty))
        draw.rectangle((tx, ty, tx + tile.width - 1, ty + tile.height - 1), outline=LINE)

    draw.line((48, 2110, 1792, 2110), fill=LINE, width=1)
    draw.text((48, 2133), "Source: British Columbia: Software Developers 1991, back cover (PDF page 146).", font=font(18), fill=MUTED)
    draw.text((48, 2162), "Rendering and enlargement reveal alignment; they do not add historical detail. Typography is unchanged in this review.", font=font(17), fill=MUTED)
    return canvas


def image_uri(image, size=None, flat_colour=None):
    if size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    if flat_colour:
        # Keep only meaningful alpha variation; premultiplied resampling can add
        # hundreds of invisible RGB variations and needlessly enlarge the HTML.
        alpha = image.getchannel("A")
        image = Image.new("RGBA", image.size, (*flat_colour, 0))
        image.putalpha(alpha)
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()


def svg_uri(data):
    return "data:image/svg+xml;base64," + base64.b64encode(data).decode()


def html_viewer(scan, before_bytes, after_bytes, before_edge, after_edge, hashes):
    data = {
        "source": image_uri(scan), "before": svg_uri(before_bytes), "after": svg_uri(after_bytes),
        "beforeOutline": image_uri(before_edge, (1568, 1744), MAGENTA),
        "afterOutline": image_uri(after_edge, (1568, 1744), CYAN),
        "points": POINTS, "hashes": hashes,
    }
    point_buttons = "".join(f'<button class="point" data-point="{p["number"]}"><b>{p["number"]}</b><span>{html.escape(p["name"])}</span></button>' for p in POINTS)
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BC Trade - registered flag overlay</title>
<style>
:root{color-scheme:light;--paper:#f5f4ef;--ink:#172d48;--muted:#53616a;--line:#d8dede;--before:#cb239d;--after:#009cb9}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:32px 28px 40px}.eyebrow{font-size:12px;letter-spacing:.12em;font-weight:750;color:var(--muted)}h1{font-size:clamp(28px,4vw,42px);line-height:1.12;margin:10px 0 14px}p{margin:10px 0;color:var(--muted)}.lead{max-width:1000px;font-size:17px}.controls{display:flex;gap:18px 26px;align-items:flex-end;flex-wrap:wrap;background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px;margin:24px 0 18px}.field{display:flex;flex-direction:column;gap:6px}.field>span,.field>label{font-size:12px;text-transform:uppercase;letter-spacing:.06em;font-weight:700}.segmented{display:flex;gap:0}button,select{font:inherit;color:var(--ink);border:1px solid #bdc8cc;background:#fff;padding:8px 12px;cursor:pointer;border-radius:6px}button:hover{background:#edf2f4}button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:white}.segmented button{border-radius:0;margin-right:-1px}.segmented button:first-child{border-radius:6px 0 0 6px}.segmented button:last-child{border-radius:0 6px 6px 0}.opacity{min-width:180px}input[type=range]{width:185px;accent-color:var(--ink);margin:6px 0}input[type=checkbox]{accent-color:var(--ink)}.checks{display:flex;flex-direction:column;gap:7px}.checks label{font-size:14px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 285px;gap:24px;align-items:start}.viewer{min-width:0}.legend{display:flex;gap:20px;align-items:center;flex-wrap:wrap;font-size:14px;margin-bottom:12px}.key{display:inline-flex;align-items:center;gap:8px}.swatch{display:inline-block;width:25px;height:3px;background:var(--before)}.after{background:var(--after)}.stage{position:relative;overflow:hidden;width:100%;background:white;border:1px solid var(--line);border-radius:8px;isolation:isolate}.plane{position:absolute}.plane>img,.plane>svg{position:absolute;width:100%;height:100%;left:0;top:0;display:block}.source{image-rendering:pixelated}.anchors{pointer-events:none;overflow:visible}.caption{font-size:13px;margin-top:10px}.point-list{display:grid;gap:7px}.point{display:flex;align-items:center;gap:10px;text-align:left;padding:10px;font-size:14px}.point b{display:inline-grid;place-items:center;border-radius:50%;background:#e7ecee;min-width:25px;height:25px;font-size:12px}.point[aria-pressed=true] b{background:white;color:var(--ink)}aside h2{font-size:18px;margin:0 0 12px}.note{margin-top:22px;border-top:1px solid var(--line);padding-top:16px}.note h3{font-size:15px;margin:0 0 6px}.note p{font-size:13px;margin:0}.provenance{border-top:1px solid var(--line);margin-top:28px;padding-top:16px;font-size:13px;color:var(--muted)}.provenance p{margin:4px 0}code{font-size:12px;overflow-wrap:anywhere}a{color:var(--ink)}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #e4b747;outline-offset:3px}@media(max-width:900px){.layout{grid-template-columns:1fr}.point-list{grid-template-columns:repeat(2,minmax(0,1fr))}.note{max-width:700px}}@media(max-width:550px){main{padding:22px 16px}.controls{gap:16px;padding:14px}.field{width:auto}.opacity{flex:1}.checks{width:100%;flex-direction:row;gap:18px}.point-list{grid-template-columns:1fr}.legend{gap:12px}}
</style></head><body><main>
<div class="eyebrow">POFBC / REGISTERED REFERENCE REVIEW</div>
<h1>BC Trade / flag overlay</h1>
<p class="lead">Inspect the two vector revisions directly over the original scan. Magenta shows the previous visible boundaries; cyan shows the corrected boundaries. All three use the same fixed registration.</p>
<section class="controls" aria-label="Overlay controls">
 <div class="field"><span>Revision</span><div class="segmented" role="group" aria-label="Visible revision"><button data-revision="before" aria-pressed="false">Before</button><button data-revision="after" aria-pressed="false">After</button><button data-revision="both" aria-pressed="true">Both</button></div></div>
 <div class="field"><span>Display</span><div class="segmented" role="group" aria-label="Vector display"><button data-mode="outline" aria-pressed="true">Outlines</button><button data-mode="fill" aria-pressed="false">Filled artwork</button></div></div>
 <div class="field opacity"><label for="opacity">Vector opacity <output id="opacity-value">88%</output></label><input id="opacity" type="range" min="0" max="100" value="88"></div>
 <div class="field"><label for="crop">Crop</label><select id="crop"><option value="flag">Flag</option><option value="symbol">Whole emblem</option><option value="full">Full artboard</option><option value="detail" disabled>Selected inspection area</option></select></div>
 <div class="checks"><label><input id="source-toggle" type="checkbox" checked> Original scan</label><label><input id="anchor-toggle" type="checkbox" checked> Inspection anchors</label></div>
 <button id="reset" type="button">Reset view</button>
</section>
<div class="layout"><section class="viewer" aria-label="Registered overlay">
 <div class="legend"><span class="key"><i class="swatch"></i>Before</span><span class="key"><i class="swatch after"></i>After</span><span id="mode-note">Visible outlines; matching contours may overlap.</span></div>
 <div id="stage" class="stage"><div id="plane" class="plane"><img id="source" class="source" alt="Original 1991 logo scan"><img id="before" alt="Previous vector revision overlay"><img id="after" alt="Corrected vector revision overlay"><svg id="anchors" class="anchors" viewBox="0 0 784 872" aria-hidden="true"></svg></div></div>
 <p id="caption" class="caption" aria-live="polite"></p>
</section><aside><h2>Inspect a junction</h2><div class="point-list">__POINT_BUTTONS__</div>
 <section class="note"><h3>Registration stays fixed</h3><p>One source pixel maps to 4 SVG units. Both vectors retain their 784 × 872 artboard. There is no independent fitting, rotation, skew or warping.</p></section>
 <section class="note"><h3>Visible boundaries only</h3><p>Outlines are derived from high-resolution renders of the finished artwork. Covered paths and invisible white-on-white construction edges are excluded.</p></section>
 <section class="note"><h3>Scan blur is not a radius</h3><p>The original is only 196 × 218 pixels and is already blurred. Soft pixels do not establish that every original corner was rounded. Enlarged source pixels are deliberately visible. Numbered anchors locate areas for inspection.</p></section>
</aside></div>
<footer class="provenance"><p>Source: <a href="https://publications.gc.ca/collections/collection_2019/isde-ised/Iu44-114-1991-eng.pdf#page=146">British Columbia: Software Developers 1991, back cover (PDF page 146)</a>. Typography is unchanged in this review.</p><p>All viewer images are embedded; this page works offline. Opening the source link requires a connection.</p><p>Before SHA-256: <code id="before-hash"></code><br>After SHA-256: <code id="after-hash"></code></p></footer>
</main><script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent);
const q=id=>document.getElementById(id);
const state={revision:'both',mode:'outline',opacity:88,crop:'flag',point:null};
const crops={flag:[62,392,690,746],symbol:[52,28,748,746],full:[0,0,784,872]};
q('source').src=data.source;q('before-hash').textContent=data.hashes.before;q('after-hash').textContent=data.hashes.after;
q('anchors').innerHTML=data.points.map(p=>`<g><circle cx="${p.x}" cy="${p.y}" r="6" fill="none" stroke="#172d48" stroke-width="1.3"/><path d="M${p.x},${p.y} L${p.badge[0]},${p.badge[1]}" fill="none" stroke="#172d48" stroke-width="1"/><circle cx="${p.badge[0]}" cy="${p.badge[1]}" r="10" fill="#172d48"/><text x="${p.badge[0]}" y="${p.badge[1]+3.7}" text-anchor="middle" fill="white" font-family="system-ui,sans-serif" font-size="10" font-weight="700">${p.number}</text></g>`).join('');
function render(){
 const detail=state.point?data.points.find(p=>p.number===state.point):null;
 const box=detail?[detail.x-detail.size[0]/2,detail.y-detail.size[1]/2,detail.x+detail.size[0]/2,detail.y+detail.size[1]/2]:crops[state.crop];
 const w=box[2]-box[0],h=box[3]-box[1];
 q('stage').style.aspectRatio=`${w}/${h}`;Object.assign(q('plane').style,{left:`${-box[0]/w*100}%`,top:`${-box[1]/h*100}%`,width:`${784/w*100}%`,height:`${872/h*100}%`});
 for(const which of ['before','after']){q(which).src=state.mode==='outline'?data[which+'Outline']:data[which];q(which).style.opacity=(state.revision==='both'||state.revision===which)?state.opacity/100:0;}
 q('source').style.visibility=q('source-toggle').checked?'visible':'hidden';q('anchors').style.visibility=q('anchor-toggle').checked?'visible':'hidden';
 document.querySelectorAll('[data-revision]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.revision===state.revision)));
 document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode)));
 document.querySelectorAll('[data-point]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.point)===state.point)));
 q('crop').value=detail?'detail':state.crop;q('opacity-value').textContent=state.opacity+'%';q('opacity').value=state.opacity;
 q('mode-note').textContent=state.mode==='outline'?'Visible outlines; matching contours may overlap.':'Actual logo colours, superimposed at the chosen opacity.';
 const scale=q('stage').getBoundingClientRect().width/(w/4);
 q('caption').textContent=(detail?`Inspection ${detail.number}: ${detail.name}, anchor (${detail.x}, ${detail.y}). `:`${state.crop==='flag'?'Flag crop':state.crop==='symbol'?'Whole emblem':'Full artboard'}. `)+`Display approximately ${scale.toFixed(1)}× native scan size. Registration remains 4 SVG units per source pixel.`;
}
document.querySelectorAll('[data-revision]').forEach(b=>b.onclick=()=>{state.revision=b.dataset.revision;render();});
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{state.mode=b.dataset.mode;render();});
document.querySelectorAll('[data-point]').forEach(b=>b.onclick=()=>{state.point=Number(b.dataset.point);render();});
q('opacity').oninput=e=>{state.opacity=Number(e.target.value);render();};q('crop').onchange=e=>{state.crop=e.target.value;state.point=null;render();};
q('source-toggle').onchange=render;q('anchor-toggle').onchange=render;
q('reset').onclick=()=>{Object.assign(state,{revision:'both',mode:'outline',opacity:88,crop:'flag',point:null});q('source-toggle').checked=true;q('anchor-toggle').checked=true;render();};
window.addEventListener('resize',render);render();
window.bcTradeOverlay={state,hashes:data.hashes,registration:{scan:[196,218],artboard:[784,872],unitsPerPixel:4},render};
</script></body></html>'''
    return template.replace("__POINT_BUTTONS__", point_buttons).replace("__DATA__", json.dumps(data, separators=(",", ":")))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", type=Path, required=True, help="Previous SVG on the unchanged 784 x 872 artboard")
    args = parser.parse_args()
    before_path = args.before.resolve()
    for file in (before_path, MASTER):
        verify_artboard(file)
    scan = Image.open(SCAN).convert("RGB")
    if scan.size != (196, 218):
        raise ValueError(f"Expected the original 196 x 218 source; found {scan.size}")
    before_bytes, after_bytes = before_path.read_bytes(), MASTER.read_bytes()
    hashes = {"before": digest(before_bytes), "after": digest(after_bytes), "scan": digest(SCAN.read_bytes())}
    with tempfile.TemporaryDirectory(prefix="bc-trade-overlay-") as temp:
        # Render the exact hashed snapshots even if another edit is in progress.
        before_snapshot, after_snapshot = Path(temp) / "before.svg", Path(temp) / "after.svg"
        before_snapshot.write_bytes(before_bytes)
        after_snapshot.write_bytes(after_bytes)
        before = render(before_snapshot, Path(temp) / "before.png")
        after = render(after_snapshot, Path(temp) / "after.png")
        before_edge, after_edge = visible_outline(before, MAGENTA), visible_outline(after, CYAN)
        review = PACKAGE / "review"
        review.mkdir(exist_ok=True)
        sheet = review / "flag-overlay.webp"
        viewer = review / "flag-overlay.html"
        static_sheet(scan, before, after, before_edge, after_edge, hashes).save(sheet, "WEBP", lossless=True, method=6)
        viewer.write_text(html_viewer(scan, before_bytes, after_bytes, before_edge, after_edge, hashes), encoding="utf-8")
    print(json.dumps({"outputs": [str(sheet), str(viewer)], "hashes": hashes,
                      "registration": "Fixed 4 SVG units per original source pixel; no independent transform",
                      "outlineMethod": "Visible colour boundaries from 3x flattened Inkscape renders"}, indent=2))


if __name__ == "__main__":
    main()
