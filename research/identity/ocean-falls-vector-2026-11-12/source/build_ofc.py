#!/usr/bin/env python3
"""Reconstruct the OFC monogram from an explicit, manually authored geometric model.

No raster-to-vector tracing is used.  The three contours below are drawn in an
upright construction space, then sheared by a shared slope.  The source images
are only used by the separate comparison script; this builder never reads them.
"""
from pathlib import Path
import argparse
import math
import json
import xml.etree.ElementTree as ET

from svgpathtools import parse_path, Path as SVGPath, Line, CubicBezier, QuadraticBezier

SHEAR = 0.562

# Units correspond to the 747 x 341 official CIPO reproduction.  Measurements
# guide the proportions, but these are newly authored smooth shapes.
LETTER_PATHS = {
    'O': '''M 202 47
        H 386
        C 397.5 47 413.5 66.5 413.5 80
        L 412 253
        C 412 272.5 401 284 382.5 284
        H 205
        C 194.5 284 175.5 260 175.5 250
        V 77
        C 175.5 58.5 185.5 47 202 47 Z
        M 290 90.5
        H 308
        C 318.5 90.5 324.5 96.5 324.5 106
        V 224
        C 324.5 235 316 241 302.5 241
        H 286
        C 275 241 269.5 236.5 269.5 228
        V 111
        C 269.5 98 277 90.5 290 90.5 Z''',
    'F': '''M 456 40
        H 725.5
        Q 729 40 729 44
        V 81
        Q 729 86 725 86
        H 542
        C 527 86 519 99 519 114
        V 281
        H 431
        V 79
        C 431 58 442 40 456 40 Z''',
    'C': '''M 559 100
        H 728.5
        Q 729 100 729 101
        V 136
        Q 729 141 725 141
        H 650
        C 634 141 626 152 626 169
        V 213
        C 626 222 643 235 650 235
        H 728.5
        V 279
        H 563
        C 552 279 540.5 259 540.5 251
        V 125
        C 540.5 110 548 100 559 100 Z''',
}

def shear_point(p):
    return complex(p.real - SHEAR * p.imag, p.imag)

def transformed_path(d):
    result = SVGPath()
    for seg in parse_path(d):
        if isinstance(seg, Line):
            new = Line(shear_point(seg.start), shear_point(seg.end))
        elif isinstance(seg, CubicBezier):
            new = CubicBezier(*(shear_point(p) for p in (seg.start, seg.control1, seg.control2, seg.end)))
        elif isinstance(seg, QuadraticBezier):
            new = QuadraticBezier(*(shear_point(p) for p in (seg.start, seg.control, seg.end)))
        else:
            raise ValueError(type(seg))
        result.append(new)
    # Retain the last curved segment explicitly before Z.  Some SVG serializer
    # versions replace any closing segment with Z, which would lose its curve.
    def fmt(p):
        return f'{p.real:.3f},{p.imag:.3f}'.replace('.000', '')
    pieces=[]
    for sub in result.continuous_subpaths():
        pieces.append('M '+fmt(sub.start))
        for seg in sub:
            if isinstance(seg, Line):
                pieces.append('L '+fmt(seg.end))
            elif isinstance(seg, CubicBezier):
                pieces.append('C '+' '.join(fmt(p) for p in (seg.control1,seg.control2,seg.end)))
            else:
                pieces.append('Q '+' '.join(fmt(p) for p in (seg.control,seg.end)))
        if sub.isclosed():
            pieces.append('Z')
    return ' '.join(pieces)

def svg_text(fill='#000000', aligned=False):
    viewbox = '0 0 747 341' if aligned else '12 20 713 284'
    width, height = (747,341) if aligned else (1426,568)
    paths='\n'.join(f'    <path id="letter-{name}" inkscape:label="{name}" fill-rule="evenodd" d="{transformed_path(d)}"/>' for name,d in LETTER_PATHS.items())
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}" height="{height}" viewBox="{viewbox}" role="img" aria-labelledby="title desc">
  <title id="title">Ocean Falls Corporation - reconstructed OFC monogram</title>
  <desc id="desc">New vector reconstruction from the supplied CIPO trademark reproduction, application 0390863. Three manually constructed letter paths, common 0.562 shear (29.34 degrees), smooth custom curves. No autotracing, embedded raster, font dependency, or white cover-up shape. This is a reconstruction, not recovered original master artwork.</desc>
  <g id="OFC-monogram" inkscape:label="OFC monogram" fill="{fill}">
{paths}
  </g>
</svg>
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'Ocean_Falls_OFC.svg').write_text(svg_text(),encoding='utf-8')
    (args.out/'Ocean_Falls_OFC_white.svg').write_text(svg_text('#FFFFFF'),encoding='utf-8')
    (args.out/'verification').mkdir(exist_ok=True)
    (args.out/'verification'/'OFC_source_aligned.svg').write_text(svg_text(aligned=True),encoding='utf-8')
    params={'reconstruction':True,'method':'manually authored paths in upright construction space with shared shear',
            'shear':SHEAR,'angle_degrees_from_vertical':math.degrees(math.atan(SHEAR)),
            'source_canvas':[747,341],'paths_upright':LETTER_PATHS,
            'source_coordinate_space':'x = u - 0.562*y; y = y',
            'intentionally_retained':'CIPO top/baseline offsets, broad diagonal strokes and thinner horizontal bars',
            'not_established':'original designer, exact historical construction rules, original colour specification'}
    (args.out/'source').mkdir(exist_ok=True)
    (args.out/'source'/'geometry.json').write_text(json.dumps(params,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(args.out),'angle':params['angle_degrees_from_vertical'],'path_count':len(LETTER_PATHS)}))

if __name__=='__main__':
    main()
