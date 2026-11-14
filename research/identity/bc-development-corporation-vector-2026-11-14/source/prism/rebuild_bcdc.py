#!/usr/bin/env python3
"""Rebuild the BCDC artwork from geometry and font outlines, without tracing.

Requires Python, fontTools, Pillow, and Inkscape. PDF packaging also uses PyMuPDF.
Fonts are read from the local system; no font files are distributed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = Path('/usr/share/fonts/opentype/urw-base35')
PARAMS = {
    'face_side': 60.0,
    'diagonal_extension': 57.5,
    'line_weight': 11.5,
    'central_clear_gap': 22.0,
    'base_width': 280.0,
    'vertical_scale': 15 / 14,
    'mark_height': 300.0,
    'name_left': 308.0,
    'name_font_size_before_vertical_scale': 66.0,
    'name_baselines_before_vertical_scale': [60.0, 128.5, 197.0, 265.5],
    'name_optical_widths': [176.0, 260.0, 344.0, 312.0],
    'name_font': 'Nimbus Roman Regular (approximation; original unidentified)',
    'name_optical_spread_per_side': 0.35,
    'address_font': 'Nimbus Roman Bold Italic (approximation)',
}


def num(value):
    v = 0 if abs(value) < 0.0000001 else value
    return f'{v:.5f}'.rstrip('0').rstrip('.')


def offset_polygon(poly, distance):
    """Parallel offset of a convex polygon with exact miter intersections."""
    edges = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        q = (a[0] + distance * dy / length, a[1] - distance * dx / length)
        edges.append((q, (dx, dy)))
    out = []
    for i in range(len(edges)):
        a, u = edges[i - 1]
        b, v = edges[i]
        cross = u[0] * v[1] - u[1] * v[0]
        t = ((b[0] - a[0]) * v[1] - (b[1] - a[1]) * v[0]) / cross
        out.append((a[0] + t * u[0], a[1] + t * u[1]))
    return out


def master_polygons():
    s, d, t = (PARAMS[k] for k in ['face_side', 'diagonal_extension', 'line_weight'])
    outer = [(0, 0), (s, 0), (s + d, d), (s + d, s + d), (d, s + d), (0, s)]
    faces = [
        [(0, 0), (s, 0), (s, s), (0, s)],
        [(s, 0), (s + d, d), (s + d, s + d), (s, s)],
        [(0, s), (s, s), (s + d, s + d), (d, s + d)],
    ]
    polygons = [offset_polygon(outer, t / 2)] + [offset_polygon(face, -t / 2) for face in faces]
    return [[(x + t / 2, y + t / 2) for x, y in poly] for poly in polygons]


def transform_polygon(poly, quadrant):
    angle = quadrant * math.pi / 2
    co, si = round(math.cos(angle)), round(math.sin(angle))
    out = []
    for x, y in poly:
        x, y = x - 140, y - 140
        out.append((140 + co * x - si * y, (140 + si * x + co * y) * PARAMS['vertical_scale']))
    return out


def polygon_d(poly):
    return 'M' + ' L'.join(f'{num(x)} {num(y)}' for x, y in poly) + ' Z'


def mark_group(color='#000000'):
    names = ['north-west', 'north-east', 'south-east', 'south-west']
    master = master_polygons()
    paths = []
    for k, name in enumerate(names):
        d = ' '.join(polygon_d(transform_polygon(poly, k)) for poly in master)
        paths.append(f'<path id="prism-{name}" d="{d}"/>')
    return f'<g id="symbol" fill="{color}" fill-rule="evenodd">' + ''.join(paths) + '</g>'


class OutlineFont:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font['head'].unitsPerEm
        self.metrics = ImageFont.truetype(str(path), self.upem)

    def positioned_glyphs(self, text):
        x = 0.0
        for i, ch in enumerate(text):
            yield ch, self.glyphs[self.cmap[ord(ch)]], x
            if i + 1 < len(text):
                x += self.metrics.getlength(ch + text[i + 1]) - self.metrics.getlength(text[i + 1])

    def outline(self, text, left, baseline, size, target_width=None, group_id='text-line', spread=0):
        bounds = BoundsPen(self.glyphs)
        positioned = list(self.positioned_glyphs(text))
        for ch, glyph, x in positioned:
            glyph.draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x0, y0, x1, y1 = bounds.bounds
        sx = size / self.upem if target_width is None else target_width / (x1 - x0)
        sy = size / self.upem * PARAMS['vertical_scale']
        result = []
        for i, (ch, glyph, x) in enumerate(positioned):
            pen = SVGPathPen(self.glyphs, ntos=num)
            glyph.draw(TransformPen(pen, (sx, 0, 0, -sy, left + (x - x0) * sx, baseline)))
            d = pen.getCommands()
            if d:
                stroke = f' stroke="#000000" stroke-width="{num(2*spread)}" stroke-linejoin="round"' if spread else ''
                result.append(f'<path id="{group_id}-{i + 1}" d="{d}"{stroke}/>')
        return f'<g id="{group_id}" aria-label="{escape(text)}">' + ''.join(result) + '</g>'


def name_group(font, color='#000000'):
    parts = []
    for i, (word, baseline, width) in enumerate(zip(
        ['British', 'Columbia', 'Development', 'Corporation'],
        PARAMS['name_baselines_before_vertical_scale'],
        PARAMS['name_optical_widths'],
    )):
        spread = PARAMS['name_optical_spread_per_side']
        parts.append(font.outline(word, PARAMS['name_left'] + spread,
                                  baseline * PARAMS['vertical_scale'] - spread,
                                  66, width - 2 * spread, f'name-line-{i + 1}', spread))
    raw = '<g id="corporation-name" fill="#000000">' + ''.join(parts) + '</g>'
    # Expand the tiny optical spread and unite it with each original glyph.
    # This keeps the production lettering as filled contours, without strokes.
    ns = {'s': 'http://www.w3.org/2000/svg'}
    with tempfile.TemporaryDirectory(prefix='bcdc-type-') as td:
        src, dst = Path(td) / 'type.svg', Path(td) / 'expanded.svg'
        src.write_text(svg_document('Type preparation', raw, 652, 300, 'Optical outline expansion'))
        root = ET.fromstring(src.read_text())
        ids = [el.attrib['id'] for el in root.findall('.//s:path', ns)]
        actions = []
        for glyph_id in ids:
            actions += ['select-clear', f'select-by-id:{glyph_id}', 'object-stroke-to-path',
                        'selection-ungroup', 'path-union']
        actions += ['export-do']
        subprocess.run(['inkscape', str(src), '--export-type=svg', '--export-plain-svg',
                        f'--export-filename={dst}', '--actions=' + ';'.join(actions)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        expanded = ET.fromstring(dst.read_text())
        groups = []
        count = 0
        for i, word in enumerate(['British', 'Columbia', 'Development', 'Corporation']):
            line = expanded.find(f'.//s:g[@id="name-line-{i + 1}"]', ns)
            paths = line.findall('.//s:path', ns)
            assert len(paths) == len(word), (word, len(paths))
            assert all('transform' not in p.attrib for p in paths)
            clean = ''.join(f'<path id="name-line-{i + 1}-{j + 1}" d="{p.attrib["d"]}"/>'
                            for j, p in enumerate(paths))
            groups.append(f'<g id="name-line-{i + 1}" aria-label="{word}">' + clean + '</g>')
            count += len(paths)
        assert count == 37
    return f'<g id="corporation-name" fill="{color}">' + ''.join(groups) + '</g>'


def address_group(font):
    lines = ['272 Granville Square,', '200 Granville Street,', 'Vancouver, B.C.']
    parts = [font.outline(line, 310, base * PARAMS['vertical_scale'], 37.5,
                          None, f'address-line-{i + 1}')
             for i, (line, base) in enumerate(zip(lines, [340, 375, 410]))]
    return '<g id="historical-address" fill="#000000">' + ''.join(parts) + '</g>'


def svg_document(title, body, width, height, description):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{num(width)}" height="{num(height)}" viewBox="0 0 {num(width)} {num(height)}" role="img" aria-labelledby="artwork-title artwork-description">
<title id="artwork-title">{escape(title)}</title>
<desc id="artwork-description">{escape(description)}</desc>
{body}
</svg>
'''


def write_svg(name, title, body, width, height, description):
    (HERE / name).write_text(svg_document(title, body, width, height, description), encoding='utf-8')


def render_png(svg, png, width, background=None):
    args = ['inkscape', str(svg), '--export-type=png', f'--export-filename={png}', f'--export-width={width}']
    if background:
        args += [f'--export-background={background}', '--export-background-opacity=1']
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', action='store_true', help='Also export and combine the three vector PDF artboards.')
    args = parser.parse_args()
    normal = OutlineFont(FONT_DIR / 'NimbusRoman-Regular.otf')
    italic = OutlineFont(FONT_DIR / 'NimbusRoman-BoldItalic.otf')
    desc = ('Geometric reconstruction from the three supplied newspaper references. '
            'Four repeated prism modules; four compound filled paths with twelve transparent face openings. '
            'This is a reconstruction, not an authenticated original master.')
    type_desc = (' Lettering is an optically fitted Nimbus Roman Regular approximation with a 0.35-unit optical spread, converted to filled outlines; '
                 'the historical typeface has not been confirmed.')
    mark = mark_group()
    name = name_group(normal)
    write_svg('BCDC-symbol.svg', 'British Columbia Development Corporation symbol', mark, 280, 300, desc)
    write_svg('BCDC-symbol-white.svg', 'BCDC symbol, white', mark_group('#ffffff'), 280, 300, desc)
    write_svg('BCDC-logo.svg', 'British Columbia Development Corporation', mark + name, 652, 300, desc + type_desc)
    write_svg('BCDC-logo-white.svg', 'British Columbia Development Corporation, white',
              mark_group('#ffffff') + name.replace('fill="#000000"', 'fill="#ffffff"'), 652, 300, desc + type_desc)
    write_svg('BCDC-historical-address.svg', 'BCDC historical advertisement lockup',
              mark + name + address_group(italic), 652, 448,
              desc + type_desc + ' Address retained as a separate historical layout, not current contact information.')

    s, d, t = (PARAMS[k] for k in ['face_side', 'diagonal_extension', 'line_weight'])
    centerline = f'M0 0 H{num(s)} L{num(s+d)} {num(d)} V{num(s+d)} H{num(d)} L0 {num(s)} Z M0 {num(s)} H{num(s)} V0 M{num(s)} {num(s)} L{num(s+d)} {num(s+d)}'
    master = f'<defs><g id="one-prism" transform="translate({num(t/2)} {num(t/2)})"><path d="{centerline}"/></g></defs>'
    uses = ''.join(f'<use href="#one-prism" transform="rotate({k*90} 140 140)"/>' for k in range(4))
    body = master + f'<g fill="none" stroke="#000000" stroke-width="{num(t)}" stroke-linecap="butt" stroke-linejoin="miter" transform="scale(1 {num(PARAMS["vertical_scale"])})">{uses}</g>'
    write_svg('BCDC-symbol-construction.svg', 'BCDC editable geometric construction', body, 280, 300,
              'Editable stroke-based master. One prism is repeated at quarter turns in the square base system, then the whole symbol is scaled vertically by 15/14. Use the expanded symbol for production.')

    (HERE / 'BCDC-construction.json').write_text(json.dumps(PARAMS, indent=2) + '\n')
    render_png(HERE / 'BCDC-symbol.svg', HERE / 'BCDC-symbol.png', 1120)
    render_png(HERE / 'BCDC-logo.svg', HERE / 'BCDC-logo.png', 2608)
    preview = '<rect width="1560" height="760" fill="#ffffff"/><g transform="translate(100 67.11656) scale(2.08588957)">' + mark + name + '</g>'
    preview_svg = HERE / 'BCDC-preview.svg'
    preview_svg.write_text(svg_document('BCDC reconstructed logo preview', preview, 1560, 760, desc + type_desc))
    render_png(preview_svg, HERE / 'BCDC-preview.png', 1560)

    if args.pdf:
        import fitz
        result = fitz.open()
        with tempfile.TemporaryDirectory(prefix='bcdc-pdf-') as td:
            for stem in ['BCDC-symbol', 'BCDC-logo', 'BCDC-historical-address']:
                out = Path(td) / (stem + '.pdf')
                subprocess.run(['inkscape', str(HERE / (stem + '.svg')), '--export-type=pdf',
                                f'--export-filename={out}', '--export-text-to-path'], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                doc = fitz.open(out)
                result.insert_pdf(doc)
                doc.close()
        result.set_metadata({'title': 'British Columbia Development Corporation - reconstructed vector artwork',
                             'subject': 'Three vector artboards: symbol, serif logo, historical address layout',
                             'creator': 'Parametric geometric reconstruction; no raster tracing',
                             'keywords': 'BCDC, vector, reconstruction, British Columbia Development Corporation'})
        result.save(HERE / 'BCDC-vector-artwork.pdf', deflate=True)
        result.close()
    print('Wrote BCDC SVG artwork, transparent PNGs, preview, and construction parameters.' + (' PDF exported.' if args.pdf else ''))


if __name__ == '__main__':
    main()
