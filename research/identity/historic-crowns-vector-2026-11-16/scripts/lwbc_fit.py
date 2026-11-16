"""LWBC 2004 lockup: emblem geometry and lettering fitted by overlap to the 2004/05 annual-report
cover image (371 x 180 embedded JPEG, xref 4008 of lwbc-2004spr.pdf)."""
import sys, json, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit, raster, iou, fit_text, init_text, raster_eo
SRC = sys.argv[1]
a = np.array(Image.open(SRC).convert('RGB')).astype(float)
H, W, _ = a.shape
def near(c, tol=45): return np.sqrt(((a - np.array(c))**2).sum(2)) < tol
ink = a.min(2) < 200
olive = near((176, 172, 48), 50)
teal = near((37, 86, 98), 55)
black = a.max(2) < 90
res = {}
# emblem square minus triangle
def sq(p):
    x0, y0, x1, y1, ay = p['x0'], p['y0'], p['x1'], p['y1'], p['ay']
    xm = (x0 + x1)/2
    left = [(x0, y0), (xm, y0), (xm, y0 + ay), (x0, y1)]
    right = [(xm, y0), (x1, y0), (x1, y1), (xm, y0 + ay)]
    return [left, right]
o = olive.copy(); o[:, 115:] = False
b, s = fit(sq, dict(x0=41, y0=38, x1=107, y1=100, ay=0), dict(x0=1, y0=1, x1=1, y1=1), o)
res['square'] = dict(b, iou=s); print('square', s, b)
def circ(p, n=72): return [[(p['cx'] + p['r']*math.cos(2*math.pi*i/n), p['cy'] + p['r']*math.sin(2*math.pi*i/n)) for i in range(n)]]
t = teal.copy(); t[:, 115:] = False; t[:70, :] = False; t[105:, :] = False
b, s = fit(circ, dict(cx=75, cy=87, r=16), dict(cx=1, cy=1, r=1), t)
res['circle'] = dict(b, iou=s); print('circle', s, b)
# waves: centreline cubic from (x0,yl) to (x1,yr) with control ys, constant vertical thickness th
def bez(p0, p1, p2, p3, n=40):
    return [tuple((1-t)**3*p0[i] + 3*(1-t)**2*t*p1[i] + 3*(1-t)*t*t*p2[i] + t**3*p3[i] for i in (0, 1)) for t in [k/n for k in range(n+1)]]
def wave(p):
    x0, x1 = p['x0'], p['x1']; L = x1 - x0
    c = bez((x0, p['yl']), (x0 + L/3, p['c1']), (x0 + 2*L/3, p['c2']), (x1, p['yr']))
    h = p['th']/2
    return [[(x, y - h) for x, y in c] + [(x, y + h) for x, y in reversed(c)]]
region = (a.min(2) < 225); region[:, 112:] = False; region[:106, :] = False; region[160:, :] = False
X = np.arange(W)[None, :].repeat(H, 0); Y = np.arange(H)[:, None].repeat(W, 1)
s1 = 124 + (X - 50)*0.14; s2 = 139 + (X - 50)*0.14
sel = [region & (Y < s1), region & (Y >= s1) & (Y < s2), region & (Y >= s2)]
init = [(114.5, 122, 9), (131, 138.5, 6), (144.5, 152, 4)]
waves = []
for i, m in enumerate(sel):
    yl, yr, th = init[i]
    b, s = fit(wave, dict(x0=41, x1=107, yl=yl, yr=yr, c1=yl+(yr-yl)/3, c2=yl+2*(yr-yl)/3, th=th), dict(x0=1, x1=1, yl=1, yr=1, c1=2, c2=2, th=0.5), m)
    core = raster(wave(dict(b, th=max(1, b['th']-3))), (W, H)) & m
    col = np.median(a[core], 0)
    waves.append(dict(b, iou=s, colour=[float(v) for v in col])); print('wave', i, round(s, 3), col, {k: round(v, 2) for k, v in b.items()})
res['waves'] = waves
json.dump(res, open(sys.argv[2], 'w'), indent=0, default=float)
