import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from textpath import layout, path_d, polys
from uta_arrow import model
from svgout import write, poly_d
from fitlib import raster_eo, overlay_sheet
FONT = '/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'
SRC = '/home/user/PofBC/public/identity-collected/urban-transit-authority/urban-transit-authority-1980-regional-signature.png'
r = json.load(open(sys.argv[1])); ink = '#000000'
shapes = []; allp = []
for k in ('line1', 'line2'):
    p = r[k]; pl, _ = layout(p['text'], FONT, p['size'], p['x'] + p['ox'], p['y'] + p['oy'], p['tracking'])
    shapes.append((path_d(pl, FONT), ink)); allp += polys(pl, FONT)
a = dict(r['arrow']); a['cx'] += a['ox']; a['cy'] += a['oy']; a['xr'] += a['ox']; a['ys'] += a['oy']
for q in model(a): shapes.append((poly_d(q), ink)); allp.append(q)
xs = [x for q in allp for x, y in q]; ys = [y for q in allp for x, y in q]
print(write(sys.argv[2], shapes, (min(xs), min(ys), max(xs), max(ys)), 'Capital Regional District / Urban Transit Authority signature (reconstruction)'))
overlay_sheet(SRC, raster_eo(allp, (1030, 245)), sys.argv[3], thr=120)
