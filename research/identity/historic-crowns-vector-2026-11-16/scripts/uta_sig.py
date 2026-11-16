"""UTA 1980 regional signature: Helvetica-Bold-like lines (Nimbus Sans Bold outlines) and the
double arrow, each fitted by overlap to the 1980 Daily Colonist scan."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from fitlib import mask_of, fit_text, fit, raster, iou, init_text
from uta_arrow import model
SRC = '/home/user/PofBC/public/identity-collected/urban-transit-authority/urban-transit-authority-1980-regional-signature.png'
FONT = '/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'
m = mask_of(SRC, 120)
def ext(r):
    ys, xs = np.where(r); return xs.min(), xs.max(), ys.min(), ys.max()
res = {}
for key, text, (y0, y1, x0, x1) in [('line1', 'Capital Regional District', (66, 110, 0, 400)), ('line2', 'Urban Transit Authority', (118, 162, 628, 1012))]:
    r = m[y0:y1, x0:x1].copy(); a, b, t, bt = ext(r)
    # cap height: rows of the first capital's column band
    first = r[:, a:a+12]; fy = np.where(first.any(1))[0]
    p0 = init_text(text, FONT, r, fy.max() - fy.min() + 1, fy.max() + 0.5, a, b + 1)
    best, s, _ = fit_text(text, FONT, r, p0, dict(x=1, y=1, size=0.5, tracking=6))
    res[key] = dict(best, oy=y0, ox=x0, iou=s, text=text); print(key, best, s)
ra = m[:, 400:620].copy(); ra[:, :8] = False
p0 = dict(cx=110, cy=124, g=5, W=105, H=105, t=32, ys=75, xr=170)
ba, sa = fit(model, p0, dict(cx=2, cy=2, g=1, W=2, H=2, t=2, ys=2, xr=2), ra)
res['arrow'] = dict(ba, ox=400, oy=0, iou=sa)
json.dump(res, open(sys.argv[1], 'w'), indent=0)
