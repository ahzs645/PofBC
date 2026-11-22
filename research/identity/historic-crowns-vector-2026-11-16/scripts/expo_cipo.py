"""EXPO 86 stacked symbol, rebuilt from the CIPO 901519 drawing (1982): the 86 as three elliptical
rings and a bar, the EXPO letters as round-ended monoline strokes, each primitive fitted by overlap."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit_prims, raster_prims, iou, overlay_sheet
from prims import annulus, capsule, bar, ellipse_pts
SRC = '/home/user/PofBC/public/identity-collected/expo-86-corporation/expo86-cipo-1982.png'
m = np.array(Image.open(SRC).convert('L')) < 128; H, W = m.shape
def rings(p):
    return [annulus(p['ax'], p['ay'], p['arx'], p['ary'], p['t']), annulus(p['bx'], p['by'], p['brx'], p['bry'], p['t']),
            annulus(p['cx'], p['cy'], p['crx'], p['cry'], p['t']), bar(p['x1'], p['y1'], p['x2'], p['y2'], p['w'])]
lower = m.copy(); lower[:180] = False
p0 = dict(ax=210, ay=365, arx=180, ary=175, bx=205, by=570, brx=180, bry=175, cx=415, cy=570, crx=175, cry=175, t=70, x1=400, y1=420, x2=560, y2=245, w=62)
st = {k: 4 for k in p0}
b86, s86 = fit_prims(rings, p0, st, lower)
print('86', round(s86, 4), {k: round(v, 1) for k, v in b86.items()})
# letters: E, X, P, O with one stroke width s each (shared)
def E(p):
    s = p['s']; x0 = p['ex'] + s/2; xr = p['ex2'] - s/2; yt = p['top'] + s/2; yb = p['bot'] - s/2; ym = p['emid']
    return [capsule(x0, yt, x0, yb, s), capsule(x0, yt, xr, yt, s), capsule(x0, ym, p['emr'] - s/2, ym, s), capsule(x0, yb, xr, yb, s)]
def X(p):
    s = p['s']; yt = p['top'] + s/2; yb = p['bot'] - s/2
    return [capsule(p['xl'] + s/2, yt, p['xr'] - s/2, yb, s*p['xk']), capsule(p['xr'] - s/2, yt, p['xl'] + s/2, yb, s*p['xk'])]
def P(p):
    s = p['s']; x0 = p['px'] + s/2; yt = p['top'] + s/2; yb = p['bot'] - s/2; yj = p['pj']
    ry = (yj - yt)/2; cy = yt + ry; cxr = p['pr'] - s/2 - ry  # bowl: straight top/bottom then half-ellipse
    arc = annulus(cxr, cy, ry + s/2, ry + s/2, s)
    right = [(cxr, cy - ry - s), (cxr + ry + s, cy - ry - s), (cxr + ry + s, cy + ry + s), (cxr, cy + ry + s)]
    import math
    outer = [pt for pt in ellipse_pts(cxr, cy, ry + s/2, ry + s/2, 0, 60, -math.pi/2, math.pi/2)]
    inner = [pt for pt in ellipse_pts(cxr, cy, ry - s/2, ry - s/2, 0, 60, -math.pi/2, math.pi/2)][::-1]
    half = (outer + inner, [])
    return [capsule(x0, yt, x0, yb, s), capsule(x0, yt, cxr, yt, s), capsule(x0, yj - s/2 + s/2, cxr, yj, s), half]
def O(p):
    return [annulus(p['ox'], (p['top'] + p['bot'])/2, p['orx'], (p['bot'] - p['top'])/2, p['s']*p['ok'])]
def letters(p): return E(p) + X(p) + P(p) + O(p)
upper = m.copy(); upper[180:] = False
q0 = dict(s=30, top=5, bot=166, ex=52, ex2=150, emid=86, emr=145, xl=164, xr=293, xk=1.0, px=300, pr=400, pj=110, ox=500, orx=77, ok=1.0)
bl, sl = fit_prims(letters, q0, {k: (0.05 if k in ('xk', 'ok') else 2) for k in q0}, upper)
print('EXPO', round(sl, 4), {k: round(v, 2) for k, v in bl.items()})
json.dump(dict(n86=b86, letters=bl, iou86=s86, iouLetters=sl), open(sys.argv[1], 'w'), indent=0)
allm = raster_prims(rings(b86) + letters(bl), (W, H)); print('total', iou(allm, m))
overlay_sheet(SRC, allm, sys.argv[2], thr=128)
