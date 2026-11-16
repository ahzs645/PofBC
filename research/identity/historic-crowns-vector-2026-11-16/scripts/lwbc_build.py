"""Build the LWBC 2004 lockup SVG from the fitted geometry (lwbc_fit.py) and lettering (lwbc_letters.py).
Coordinates are the 2004/05 cover image's pixels. Colours are medians sampled inside each fitted shape."""
import sys, json, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import raster, raster_eo
from textpath import layout, path_d, polys
from svgout import write, poly_d, num
SRC, GEO, LET, OUT, FACE = sys.argv[1:6]
U = '/usr/share/fonts/opentype/urw-base35/'; F = U + FACE + '.otf'
a = np.array(Image.open(SRC).convert('RGB')).astype(float); H, W, _ = a.shape
g = json.load(open(GEO)); L = json.load(open(LET))
hexc = lambda c: '#%02x%02x%02x' % tuple(int(round(v)) for v in c)
def med(mask): return np.median(a[mask], 0)
def bez(p0, p1, p2, p3, n=48):
    return [tuple((1-t)**3*p0[i] + 3*(1-t)**2*t*p1[i] + 3*(1-t)*t*t*p2[i] + t**3*p3[i] for i in (0, 1)) for t in [k/n for k in range(n+1)]]
shapes = []; allp = []
sq = g['square']; x0, y0, x1, y1 = sq['x0'], sq['y0'], sq['x1'], sq['y1']; xm = (x0 + x1)/2
olive_polys = [[(x0, y0), (xm, y0), (x0, y1)], [(xm, y0), (x1, y0), (x1, y1)]]
om = raster(olive_polys, (W, H))
shapes.append((''.join(poly_d(p) for p in olive_polys), hexc(med(om & (a.min(2) < 200))))); allp += olive_polys
c = g['circle']
k = 0.5523*c['r']; cx, cy, r = c['cx'], c['cy'], c['r']
circ_d = (f"M{num(cx)} {num(cy-r)}C{num(cx+k)} {num(cy-r)} {num(cx+r)} {num(cy-k)} {num(cx+r)} {num(cy)}"
          f"C{num(cx+r)} {num(cy+k)} {num(cx+k)} {num(cy+r)} {num(cx)} {num(cy+r)}"
          f"C{num(cx-k)} {num(cy+r)} {num(cx-r)} {num(cy+k)} {num(cx-r)} {num(cy)}"
          f"C{num(cx-r)} {num(cy-k)} {num(cx-k)} {num(cy-r)} {num(cx)} {num(cy-r)}Z")
cpoly = [(cx + r*math.cos(2*math.pi*i/72), cy + r*math.sin(2*math.pi*i/72)) for i in range(72)]
teal = hexc(med(raster([cpoly], (W, H)) & (a.min(2) < 160)))
shapes.append((circ_d, teal)); allp.append(cpoly)
for w in g['waves']:
    L_ = w['x1'] - w['x0']; h = w['th']/2
    P = [(w['x0'], w['yl']), (w['x0'] + L_/3, w['c1']), (w['x0'] + 2*L_/3, w['c2']), (w['x1'], w['yr'])]
    up = [(x, y - h) for x, y in P]; dn = [(x, y + h) for x, y in P]
    d = (f"M{num(up[0][0])} {num(up[0][1])}C" + ' '.join(f"{num(x)} {num(y)}" for x, y in up[1:]) +
         f"L{num(dn[3][0])} {num(dn[3][1])}C" + ' '.join(f"{num(x)} {num(y)}" for x, y in [dn[2], dn[1], dn[0]]) + 'Z')
    shapes.append((d, hexc(w['colour'])))
    allp.append([(x, y - h) for x, y in bez(*P)] + [(x, y + h) for x, y in reversed(bez(*P))])
for text, colour_mask in (('LWBC', None), ('LAND AND WATER', None), ('BRITISH COLUMBIA INC.', None)):
    R = L[text]; yA, yB, xA, xB = R['region']; p = R['res'][FACE]['p']; dx = R['res'][FACE]['dx']
    pl, _ = layout(text, F, p['size'], p['x'] + xA, p['y'] + yA, p.get('tracking', 0), p.get('hscale', 1))
    pl = [(gl, (A, B, C, D, E + dx[i], Fy)) for i, (gl, (A, B, C, D, E, Fy)) in enumerate(pl)]
    pp = polys(pl, F); tm = raster_eo(pp, (W, H))
    col = hexc(med(tm & (a.min(2) < 120)))
    shapes.append((path_d(pl, F), col, 'fill-rule="nonzero"')); allp += pp
xs = [x for q in allp for x, y in q]; ys = [y for q in allp for x, y in q]
print(write(OUT, shapes, (min(xs), min(ys), max(xs), max(ys)), 'Land and Water British Columbia Inc. (reconstruction)', scale=4))
print([s[1] for s in shapes])
json.dump({'colours': [s[1] for s in shapes]}, open(OUT + '.colours.json', 'w'))
