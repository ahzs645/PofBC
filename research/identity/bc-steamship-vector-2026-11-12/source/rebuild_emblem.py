#!/usr/bin/env python3
"""Construct the BC Steamship emblem from a small geometric model.

No reference raster is opened by this generator. The photo-coordinate values
below are manually selected design landmarks, regularized into shared circles,
straight edges, mirrored facets and circular wave segments. They are not
recovered manufacturing specifications.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
CX, CY = 254.5, 245.0
P = {
    'reference_registration': {'center_x_px': CX, 'center_y_px': CY, 'units_per_source_px': 1.0},
    'ring': {'outer_radius': 145.5, 'inner_radius': 141.8},
    'upper_envelope': {'center_y': 243.0, 'radius': 126.5},
    'stem_half_width': 19.5,
    'fan_inner_x_left': 222.0,
    'fan_baseline': 217.0,
    'upper_triangle': {'arc_corner_x': 178.0, 'inner_tip_y': 184.0},
    'diagonal_ray': {'arc_upper_x': 168.0, 'arc_lower_x': 153.5, 'inner_top_y': 200.5, 'inner_lower_x': 207.0},
    'lower_triangle': {'arc_corner_x': 146.0, 'inner_base_x': 192.0},
    'bar': {'center_y': 244.5, 'radius': 128.0, 'top': 226.0, 'bottom': 263.0},
    'first_wave': {'top': 270.0, 'center_y': 250.5, 'radius': 48.5, 'center_offset': 80.0},
    'second_wave': {'top': 306.5, 'center_y': 262.1, 'radius': 71.9, 'center_offset': 51.8},
    'bottom_segment': {'top': 342.5, 'center_y': 239.0, 'radius': 131.0},
}


def n(v):
    return f'{v:.5f}'.rstrip('0').rstrip('.')


def pt(x, y):
    return f'{n(x-CX)} {n(y-CY)}'


def circle(r):
    return f'M 0 {n(-r)} A {n(r)} {n(r)} 0 1 1 0 {n(r)} A {n(r)} {n(r)} 0 1 1 0 {n(-r)} Z'


def upper_y(x):
    e = P['upper_envelope']
    return e['center_y'] - math.sqrt(e['radius']**2 - (x-CX)**2)


def upper_left_x(y):
    e = P['upper_envelope']
    return CX - math.sqrt(e['radius']**2 - (y-e['center_y'])**2)


def arc(r, x, y, sweep=0):
    return f'A {n(r)} {n(r)} 0 0 {sweep} {pt(x,y)}'


def band(centers, center_y, radius, top):
    """Union of equal lower circular segments, with a positive cusp bridge."""
    half_chord = math.sqrt(radius**2 - (top-center_y)**2)
    x0, x1 = centers[0]-half_chord, centers[-1]+half_chord
    joints = []
    for a,b in zip(centers, centers[1:]):
        joints.append(((a+b)/2, center_y+math.sqrt(radius**2-((b-a)/2)**2)))
    pieces = [f'M {pt(x0,top)} H {n(x1-CX)}']
    for i in range(len(centers)-1, -1, -1):
        end = joints[i-1] if i else (x0,top)
        pieces.append(arc(radius,*end,sweep=1))
    return ' '.join(pieces)+' Z'


def geometry():
    e = P['upper_envelope']
    r = e['radius']
    ring = circle(P['ring']['outer_radius'])+' '+circle(P['ring']['inner_radius'])
    h = P['stem_half_width']
    xl,xr = CX-h,CX+h
    b = P['bar']
    dt = math.sqrt(b['radius']**2-(b['top']-b['center_y'])**2)
    db = math.sqrt(b['radius']**2-(b['bottom']-b['center_y'])**2)
    stem = ' '.join([
        f'M {pt(xl,upper_y(xl))}', arc(r,xr,upper_y(xr),1),
        f'V {n(b["top"]-CY)} H {n(dt)}', arc(b['radius'],CX+db,b['bottom'],1),
        f'H {n(-db)}', arc(b['radius'],CX-dt,b['top'],1),
        f'H {n(xl-CX)} Z',
    ])
    xi, baseline = P['fan_inner_x_left'],P['fan_baseline']
    a = P['upper_triangle']['arc_corner_x']
    upper = f'M {pt(xi,upper_y(xi))} {arc(r,a,upper_y(a))} L {pt(xi,P["upper_triangle"]["inner_tip_y"])} Z'
    d = P['diagonal_ray']
    a,b = d['arc_upper_x'],d['arc_lower_x']
    ray = ' '.join([
        f'M {pt(a,upper_y(a))}', arc(r,b,upper_y(b)),
        f'L {pt(d["inner_lower_x"],baseline)} H {n(xi-CX)} V {n(d["inner_top_y"]-CY)} Z',
    ])
    a = P['lower_triangle']['arc_corner_x']
    lower = f'M {pt(a,upper_y(a))} {arc(r,upper_left_x(baseline),baseline)} H {n(P["lower_triangle"]["inner_base_x"]-CX)} Z'
    w = P['first_wave']
    first = band([CX-w['center_offset'],CX,CX+w['center_offset']], w['center_y'],w['radius'],w['top'])
    w = P['second_wave']
    second = band([CX-w['center_offset'],CX+w['center_offset']], w['center_y'],w['radius'],w['top'])
    w = P['bottom_segment']
    last = band([CX],w['center_y'],w['radius'],w['top'])
    return {'outer-ring':ring,'central-stem-and-bar':stem,'left-upper-facet':upper,
            'left-diagonal-ray':ray,'left-lower-facet':lower,'three-wave-band':first,
            'two-wave-band':second,'bottom-wave-segment':last}


G = geometry()


def body(color='#000000', outline=False):
    attrs = f'fill="{color}"' if not outline else f'fill="none" stroke="{color}" stroke-width="0.65" stroke-linejoin="round"'
    result = [f'<g id="bc-steamship-emblem" {attrs}>']
    for k in ['outer-ring','central-stem-and-bar']:
        result.append(f'<path id="{k}" fill-rule="evenodd" d="{G[k]}"/>')
    for side in ['left','right']:
        transform = ' transform="scale(-1 1)"' if side=='right' else ''
        result.append(f'<g id="{side}-fan"{transform}>')
        for kind in ['upper-facet','diagonal-ray','lower-facet']:
            result.append(f'<path id="{side}-{kind}" d="{G["left-"+kind]}"/>')
        result.append('</g>')
    for k in ['three-wave-band','two-wave-band','bottom-wave-segment']:
        result.append(f'<path id="{k}" d="{G[k]}"/>')
    result.append('</g>')
    return '\n'.join(result)


def document(art,viewbox='-156 -156 312 312',width='1200',height='1200',title=None,desc=None):
    title = title or 'British Columbia Steamship Company (1975) Ltd. - reconstructed emblem'
    desc = desc or ('Constructive monochrome vector reconstruction from the supplied token photograph. '
                    'Shared circles, straight edges, mirrored facets and circular wave segments; eleven filled paths. '
                    'No bitmap, automatic contour trace or font dependency. Geometric regularization, not an original master.')
    return '\n'.join(['<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',f'<desc id="desc">{escape(desc)}</desc>',art,'</svg>',''])


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for file,color in [('bc-steamship-emblem.svg','#000000'),('bc-steamship-emblem-white.svg','#ffffff')]:
        (OUT/file).write_text(document(body(color)),encoding='utf-8')
    (HERE/'emblem-construction.json').write_text(json.dumps(P,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output_directory':str(OUT),'filled_path_count':11,'raster_images':0}))


if __name__=='__main__':
    main()
