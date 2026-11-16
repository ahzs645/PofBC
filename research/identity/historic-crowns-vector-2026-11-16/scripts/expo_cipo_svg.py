import sys, json, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from prims import d_annulus, d_capsule, d_poly, bar
from svgout import write, num
r = json.load(open(sys.argv[1])); p = r['n86']; q = r['letters']; ink = '#000000'
sh = []
for k in 'abc':
    sh.append((d_annulus(p[k + 'x'], p[k + 'y'], p[k + 'rx'], p[k + 'ry'], p['t']), ink, 'fill-rule="evenodd"'))
sh.append((d_poly(bar(p['x1'], p['y1'], p['x2'], p['y2'], p['w'])[0]), ink))
s = q['s']; yt = q['top'] + s/2; yb = q['bot'] - s/2
x0 = q['ex'] + s/2; xr = q['ex2'] - s/2
for a in [(x0, yt, x0, yb), (x0, yt, xr, yt), (x0, q['emid'], q['emr'] - s/2, q['emid']), (x0, yb, xr, yb)]: sh.append((d_capsule(*a, s), ink))
w = s*q['xk']
sh.append((d_capsule(q['xl'] + s/2, yt, q['xr'] - s/2, yb, w), ink)); sh.append((d_capsule(q['xr'] - s/2, yt, q['xl'] + s/2, yb, w), ink))
px = q['px'] + s/2; yj = q['pj']; ry = (yj - yt)/2; cy = yt + ry; cxr = q['pr'] - s/2 - ry
sh.append((d_capsule(px, yt, px, yb, s), ink)); sh.append((d_capsule(px, yt, cxr, yt, s), ink)); sh.append((d_capsule(px, yj, cxr, yj, s), ink))
Ro, Ri = ry + s/2, ry - s/2
sh.append((f"M{num(cxr)} {num(cy - Ro)}A{num(Ro)} {num(Ro)} 0 0 1 {num(cxr)} {num(cy + Ro)}L{num(cxr)} {num(cy + Ri)}A{num(Ri)} {num(Ri)} 0 0 0 {num(cxr)} {num(cy - Ri)}Z", ink))
oc = (q['top'] + q['bot'])/2
sh.append((d_annulus(q['ox'], oc, q['orx'], (q['bot'] - q['top'])/2, s*q['ok']), ink, 'fill-rule="evenodd"'))
x_min = min(q['ex'], p['bx'] - p['brx']); x_max = max(q['ox'] + q['orx'], p['cx'] + p['crx'], p['x2'] + p['w']/2)
y_min = q['top']; y_max = max(p['by'] + p['bry'], p['cy'] + p['cry'])
# bar end corners may exceed; compute
bp = bar(p['x1'], p['y1'], p['x2'], p['y2'], p['w'])[0]
x_max = max(x_max, max(x for x, y in bp)); y_min = min(y_min, min(y for x, y in bp))
print(write(sys.argv[2], sh, (x_min, y_min, x_max, y_max), 'EXPO 86 symbol, after the 1982 CIPO drawing (reconstruction)', scale=0.5))
