"""PGE circular script monogram (1935 pass/menu mark): reconstruction.

Source-pixel coordinates of the registered 300-dpi crop. The thin outer circle and the
heavy ring are circles fitted to both edges of each (720 radial samples); the script
P-G-E is an automatic potrace outline of the illustration inside the ring (disclosed).
"""
import sys, json
import numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from measure import *
from trace import upsampled_mask, trace_to_path
src, out, meta_out = sys.argv[1:4]
INK = '#1A1A1A'
g, b = load(src)
lab, st, order = comps(b)
H, W = b.shape
c = np.array([W / 2, H / 2])
ring = (lab == order[0]).astype(np.uint8)
thin = (lab == order[2]).astype(np.uint8)
o, i = radial_ring(ring, c, 100, 240); co = circle_from_polar(c, o); ci = circle_from_polar(c, i)
o2, i2 = radial_ring(thin, c, 180, 240); to = circle_from_polar(c, o2); ti = circle_from_polar(c, i2)
rc = (co[:2] + ci[:2]) / 2
yy, xx = np.mgrid[0:H, 0:W]
inside = np.hypot(xx + 0.5 - rc[0], yy + 0.5 - rc[1]) < ci[2] - 1.0
up = 4
m = upsampled_mask(g, inside, up=up, thr=128)
path, n = trace_to_path(m, up=up, turdsize=60, alphamax=1.0, opttolerance=0.2)
parts = [
    '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" stroke-width="%.2f"/>' % ((to[0] + ti[0]) / 2, (to[1] + ti[1]) / 2, (to[2] + ti[2]) / 2, INK, to[2] - ti[2]),
    '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" stroke-width="%.2f"/>' % (rc[0], rc[1], (co[2] + ci[2]) / 2, INK, co[2] - ci[2]),
    '<path fill="%s" fill-rule="evenodd" d="%s"/>' % (INK, path)]
R = to[2] + 0.5
cx, cy = (to[0] + ti[0]) / 2, (to[1] + ti[1]) / 2
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%.2f" height="%.2f">'
       '<title>Pacific Great Eastern Railway: circular script monogram</title>%s</svg>\n'
       % (cx - R, cy - R, 2 * R, 2 * R, 2 * R, 2 * R, ''.join(parts)))
open(out, 'w').write(svg)
meta = dict(thinCircle=dict(centre=[round(cx, 2), round(cy, 2)], radius=round((to[2] + ti[2]) / 2, 2), width=round(to[2] - ti[2], 2)),
            heavyRing=dict(centre=[round(rc[0], 2), round(rc[1], 2)], radius=round((co[2] + ci[2]) / 2, 2), width=round(co[2] - ci[2], 2)),
            monogramTrace=dict(tool='potracer 0.0.4', upsample=up, threshold=128, turdsize=60, alphamax=1.0, opttolerance=0.2, contours=n))
json.dump(meta, open(meta_out, 'w'), indent=1); print(meta)
