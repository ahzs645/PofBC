"""Build an SVG from fit_lines.py results: build_lines.py FIT.json FACE OUT.svg COLOUR TITLE [SRC THR OVERLAY.webp]"""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from textpath import layout, path_d, polys
from svgout import write
from fitlib import raster_eo, overlay_sheet
U = '/usr/share/fonts/opentype/urw-base35/'
fitf, face, out, colour, title = sys.argv[1:6]
F = face if face.startswith('/') else U + face + '.otf'
d = json.load(open(fitf)); shapes = []; allp = []
for text, R in d.items():
    y0, y1, x0, x1 = R['region']; p = R['res'][face]['p']; dx = R['res'][face]['dx']
    pl, _ = layout(text, F, p['size'], p['x'] + x0, p['y'] + y0, p.get('tracking', 0), p.get('hscale', 1), p.get('slant', 0))
    pl = [(g, (A, B, C, D, E + dx[i], Fy)) for i, (g, (A, B, C, D, E, Fy)) in enumerate(pl)]
    shapes.append((path_d(pl, F), colour)); allp += polys(pl, F)
xs = [x for q in allp for x, y in q]; ys = [y for q in allp for x, y in q]
print(write(out, shapes, (min(xs), min(ys), max(xs), max(ys)), title))
if len(sys.argv) > 8:
    from PIL import Image
    src, thr, ov = sys.argv[6], int(sys.argv[7]), sys.argv[8]
    W, H = Image.open(src).size
    overlay_sheet(src, raster_eo(allp, (W, H)), ov, thr=thr)
