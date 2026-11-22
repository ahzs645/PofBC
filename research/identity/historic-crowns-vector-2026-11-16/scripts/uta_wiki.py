"""Vector rebuild of the 2020 Wikimedia Commons drawing (Cjstepney) of the UTA signature:
white double arrow and two lines of Helvetica-like type (Nimbus Sans Regular) on its orange ground,
each fitted by overlap to the PNG."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit, fit_text, init_text, raster_eo, iou
from uta_arrow import model
from textpath import layout, path_d, polys
from svgout import write, poly_d, num
SRC = '/home/user/PofBC/public/identity-collected/urban-transit-authority/urban-transit-authority.png'
FONT = '/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf'
a = np.array(Image.open(SRC).convert('RGBA')).astype(int)
w = (a[:, :, 0] > 200) & (a[:, :, 1] > 200) & (a[:, :, 2] > 200)
H, W = w.shape
res = {}
ra = w.copy(); ra[:, 560:] = False
ba, sa = fit(model, dict(cx=297, cy=305, g=12, W=236, H=236, t=70, ys=190, xr=400), dict(cx=4, cy=4, g=2, W=4, H=4, t=4, ys=4, xr=4), ra)
res['arrow'] = dict(ba, iou=sa); print('arrow', sa)
def ext(r):
    ys, xs = np.where(r); return xs.min(), xs.max(), ys.min(), ys.max()
for key, text, (y0, y1, x0, x1) in [('line1', 'Urban Transit', (160, 310, 560, 1560)), ('line2', 'Authority', (310, 500, 560, 1560))]:
    r = w[y0:y1, x0:x1]; xa, xb, ya, yb = ext(r)
    first = r[:, xa:xa+40]; fy = np.where(first.any(1))[0]
    p0 = init_text(text, FONT, r, fy.max() - fy.min() + 1, fy.max() + 0.5, xa, xb + 1)
    b, s, _ = fit_text(text, FONT, r, p0, dict(x=2, y=2, size=1, tracking=5), rounds=4)
    res[key] = dict(b, ox=x0, oy=y0, text=text, iou=s); print(key, s)
json.dump(res, open(sys.argv[1], 'w'), indent=0, default=float)
# SVG: orange ground is the drawing's own rectangle
shapes = [(f'M0 0H{W}V{H}H0Z', '#d54d12')]
allp = []
for q in model(ba): shapes.append((poly_d(q), '#ffffff')); allp.append(q)
for k in ('line1', 'line2'):
    p = res[k]; pl, _ = layout(p['text'], FONT, p['size'], p['x'] + p['ox'], p['y'] + p['oy'], p['tracking'])
    shapes.append((path_d(pl, FONT), '#ffffff')); allp += polys(pl, FONT)
print(write(sys.argv[2], shapes, (0, 0, W, H), 'Urban Transit Authority signature, after the 2020 Wikimedia Commons drawing (vector rebuild)', margin=0, scale=0.5))
fm = raster_eo(allp, (W, H))
print('total IoU', iou(fm, w))
ov = np.full((H, W, 3), 255, np.uint8); ov[w & fm] = (70, 70, 70); ov[w & ~fm] = (40, 120, 235); ov[~w & fm] = (230, 40, 160)
src = Image.open(SRC).convert('RGB')
s = 240 / H; A = src.resize((round(W*s), 240)); B = Image.fromarray(ov).resize((round(W*s), 240))
sheet = Image.new('RGB', (A.width*2 + 12, 240), (235, 235, 235)); sheet.paste(A, (0, 0)); sheet.paste(B, (A.width + 12, 0)); sheet.save(sys.argv[3], quality=82)
