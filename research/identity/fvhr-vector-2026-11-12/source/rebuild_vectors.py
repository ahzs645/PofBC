#!/usr/bin/env python3
"""Rebuild the four SVG arrangements without fonts or raster tracing.

Requires Python 3 and the two adjacent lettering outline XML files.
PNG/PDF previews are exported separately from these vector arrangements.
"""
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
PARAMS = json.loads((HERE / 'reconstruction-parameters.json').read_text())


def petal(g, r, d):
    return f'M {g:.5f} {-g-d:.5f} L {g:.5f} {-g-d-2*r:.5f} A {r:.5f} {r:.5f} 0 0 1 {g+2*r:.5f} {-g-d-2*r:.5f} Z'


def emblem(mode='color', mono=False):
    p = PARAMS['reference_monochrome'] if mono else PARAMS['color_master']
    path = petal(p['g'], p['r'], p['d'])
    parts = ['<g id="emblem">']
    if mono:
        parts.append(f'<defs><clipPath id="inside-petal"><path d="{path}"/></clipPath></defs>')
    for angle in (0, 90, 180, 270):
        for reflected in (False, True):
            color = PARAMS['palette']['green' if reflected else 'blue']
            if mode == 'black' or mono:
                color = '#000000'
            if mono and reflected:
                color = p['gray']
            transform = f'rotate({angle})' + (' scale(-1 1)' if reflected else '')
            outline = ''
            if mono and reflected:
                outline = ' stroke="#000000" stroke-width="3.2" stroke-linejoin="round" clip-path="url(#inside-petal)"'
            parts.append(f'<g transform="{transform}"><path d="{path}" fill="{color}"{outline}/></g>')
    parts.append('</g>')
    return '\n'.join(parts)


def document(body, box, width, height, title):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{box}" color="#000000" role="img">
<title>{title}</title>
<desc>Geometric reconstruction from two supplied screenshots. Approximate sampled palette and Palatino-style outlined lettering; original brand specifications unverified. Transparent background.</desc>
{body}
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE.parent/'recreated-vectors')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    words = '<g id="wordmark" color="#000000">'+(HERE/'title-group.xml').read_text()+(HERE/'tagline-group.xml').read_text()+'</g>'
    for mode in ('color', 'black'):
        body = '<g transform="translate(450 450)">'+emblem(mode=mode)+'</g>'
        filename = f'fvhr-emblem-{mode}.svg'
        (args.output/filename).write_text(document(body,'0 0 900 900',900,900,f'Fraser Valley Health Region — {mode} emblem'))
    color = '<g transform="translate(112.91875 71.12581) scale(0.131707317073)">'+emblem()+'</g>'
    mono = '<g transform="translate(112.91875 71.12581) scale(1.066385385 1)">'+emblem(mono=True)+'</g>'
    for name, mark in [('color',color),('grayscale',mono)]:
        filename = f'fvhr-lockup-{name}.svg'
        (args.output/filename).write_text(document(mark+words,'45 7 856 132',1712,264,f'Fraser Valley Health Region — reconstructed {name} lockup'))
    print(f'Created four SVGs in {args.output.resolve()}')


if __name__ == '__main__':
    main()
