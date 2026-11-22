"""Fit the Compass needle geometry to TransLink's 561 x 561 needle-symbol PNG.

Model (all in source pixels):
  needle  = convex hull of a large circle (cx, cy, R) and a small corner circle (px, py, rc);
  C       = annulus about (ux, uy) with radii r1 > r2, minus the right-hand gap between two
            horizontal cuts y = yt and y = yb (x > ux).
Parameters are optimised (Nelder-Mead) for the overlap of the model with the source's blue and
white areas. Prints the fitted parameters as JSON.

    python -I compass_fit.py needle-symbol.png
"""
import sys, json
import numpy as np
from PIL import Image
from scipy.optimize import minimize

im = np.array(Image.open(sys.argv[1]).convert('RGBA')).astype(float)
A = im[:, :, 3] / 255.0
Wt = A * (im[:, :, 0] / 255.0)            # white share (blue has R = 0)
SS = 2
H = A.shape[0]
yy, xx = np.mgrid[0:H * SS, 0:H * SS] / SS + 0.5 / SS


def down(m):
    return m.reshape(H, SS, H, SS).mean((1, 3))


def hull_mask(cx, cy, R, px, py, rc):
    big = (xx - cx) ** 2 + (yy - cy) ** 2 <= R ** 2
    small = (xx - px) ** 2 + (yy - py) ** 2 <= rc ** 2
    # region between the two external tangents: union of the tangent quad
    d = np.hypot(px - cx, py - cy); ang = np.arctan2(py - cy, px - cx)
    beta = np.arccos(np.clip((R - rc) / d, -1, 1))
    pts = []
    for s in (1, -1):
        t = ang + s * beta
        pts.append((cx + R * np.cos(t), cy + R * np.sin(t)))
        pts.append((px + rc * np.cos(t), py + rc * np.sin(t)))
    quad = [pts[0], pts[1], pts[3], pts[2]]
    inside = np.ones_like(big)
    for i in range(4):
        (x1, y1), (x2, y2) = quad[i], quad[(i + 1) % 4]
        cross = (x2 - x1) * (yy - y1) - (y2 - y1) * (xx - x1)
        inside &= cross >= 0
    inside2 = np.ones_like(big)
    for i in range(4):
        (x1, y1), (x2, y2) = quad[i], quad[(i + 1) % 4]
        cross = (x2 - x1) * (yy - y1) - (y2 - y1) * (xx - x1)
        inside2 &= cross <= 0
    return big | small | inside | inside2


def c_mask(ux, uy, r1, r2, yt, yb):
    r = np.hypot(xx - ux, yy - uy)
    ring = (r <= r1) & (r >= r2)
    gap = (xx > ux) & (yy > yt) & (yy < yb)
    return ring & ~gap


def loss_needle(p):
    m = down(hull_mask(*p).astype(float))
    return -np.minimum(m, A).sum() / np.maximum(m, A).sum()


def loss_c(p):
    m = down(c_mask(*p).astype(float))
    return -np.minimum(m, Wt).sum() / np.maximum(m, Wt).sum()


n0 = [268, 291.5, 268.5, 556, 4, 4]
rn = minimize(loss_needle, n0, method='Nelder-Mead', options=dict(maxiter=600, xatol=0.05, fatol=1e-6))
ys, xs = np.where(Wt > 0.5)
# The two cuts are measured directly: summed white coverage down columns x = 400..440 puts the
# upper terminal's lower edge at y = 253.8 and the lower terminal's upper edge at y = 348.6.
YT, YB = 253.8, 348.6
c0 = [270.9, 299.3, 204.4, 116.4]
rc_ = minimize(lambda q: loss_c(list(q) + [YT, YB]), c0, method='Nelder-Mead', options=dict(maxiter=1200, xatol=0.02, fatol=1e-7))
rc_.x = list(rc_.x) + [YT, YB]
print(json.dumps(dict(needle=dict(zip(['cx', 'cy', 'R', 'px', 'py', 'rc'], [round(float(v), 3) for v in rn.x])), needleIoU=round(-rn.fun, 4),
                      C=dict(zip(['ux', 'uy', 'r1', 'r2', 'yt', 'yb'], [round(float(v), 3) for v in rc_.x])), CIoU=round(-rc_.fun, 4))))
