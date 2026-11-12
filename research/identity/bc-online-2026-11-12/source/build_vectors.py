#!/usr/bin/env python3
"""Build BC OnLine's manually reconstructed SVGs. Python standard library only.

The path data was authored as cubic Bezier silhouettes, then inspected against
aligned references. This script does not read bitmaps or extract contours.
Run: python3 source/build_vectors.py
"""
from pathlib import Path
from html import escape
import json

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
INK = 'http://www.inkscape.org/namespaces/inkscape'
BLUE_PATHS = json.loads((HERE/'emblem-paths.json').read_text())
BLACK_PATHS = json.loads((HERE/'emblem-paths-2011.json').read_text())
WORDMARK = (HERE/'wordmark-group.xml').read_text().strip()
DESCRIPTION = ('Manually reconstructed from the two supplied BC OnLine raster '
               'references. Editable cubic Bezier artwork with no embedded '
               'bitmap, automatic tracing or font dependency. This is a '
               'reconstruction, not the original official master.')

def emblem(color, transform=None, variant="blue"):
    paths = BLACK_PATHS if variant == "black" else BLUE_PATHS
    attr = f' transform="{transform}"' if transform else ''
    body = [f'<g id="emblem" inkscape:groupmode="layer" inkscape:label="Emblem" fill="{color}" fill-rule="evenodd"{attr}>']
    for shape in paths:
        body.append(f'  <path id="{shape["id"]}" inkscape:label="{escape(shape["label"],quote=True)}" d="{shape["d"]}"/>')
    body.append('</g>')
    return '\n'.join(body)

def wordmark(color):
    return WORDMARK.replace('currentColor',color).replace('<g id="wordmark"','<g id="wordmark" inkscape:groupmode="layer" inkscape:label="Wordmark"')

def svg(name, box, width, height, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="{INK}" '
            f'width="{width}" height="{height}" viewBox="{box}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{escape(name)}</title>\n'
            f'<desc id="desc">{escape(DESCRIPTION)}</desc>\n'
            f'{body}\n</svg>\n')

def write(name, content):
    (OUT/name).write_text(content)
    print(name)

for color, label in [('#333B97','blue'),('#000000','black')]:
    write(f'BC-OnLine-emblem-{label}.svg', svg(
        f'BC OnLine emblem — {label} reconstruction', '-1 -1 183 130',366,260,emblem(color,variant=label)))
write('BC-OnLine-wordmark.svg',svg('BC OnLine reconstructed wordmark','-1 38 449 68',898,136,wordmark('#000000')))
write('BC-OnLine-logo-black.svg',svg('BC OnLine reconstructed logo','-2 -2 676 151',676,151,
    wordmark('#000000')+'\n'+emblem('#000000','translate(467.25 -0.70) scale(1.13095 1.15221)',variant='black')))
