"""UTA double-arrow: two 180-degree-symmetric shapes built from 45-degree and horizontal edges,
fitted to the 1980 Daily Colonist scan (urban-transit-authority-1980-arrow.png) by overlap."""
import sys, json, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from fitlib import mask_of, fit, raster, iou
SRC = '/home/user/PofBC/public/identity-collected/urban-transit-authority/urban-transit-authority-1980-arrow.png'
def top(p):
    cx, cy, g, W, H, t, ys, xr = (p[k] for k in 'cx cy g W H t ys xr'.split())
    by = cy - g                       # bar edge
    L = (cx - W, by)                  # left tip
    A = (cx - W + H, by - H)          # apex
    C = (A[0] + t, A[1] + t)          # end of band's top edge
    N = (C[0] - ((ys) - C[1]), ys)    # inner notch, down-left at 45 deg
    R = (xr, ys)                      # end of shelf
    E = (xr + (by - ys), by)          # right tip, down-right at 45 deg
    return [L, A, C, N, R, E]
def model(p):
    a = top(p); cx, cy = p['cx'], p['cy']
    return [a, [(2*cx - x, 2*cy - y) for x, y in a]]
if __name__ == '__main__':
    m = mask_of(SRC, 140)
    # crop away the halftone border strips at left/right edges by limiting to central region
    m[:, :12] = False; m[:, 224:] = False
    p0 = dict(cx=114, cy=120, g=4.5, W=104, H=103, t=30, ys=72, xr=173)
    best, s = fit(model, p0, dict(cx=2, cy=2, g=1, W=2, H=2, t=2, ys=2, xr=2), m)
    print(json.dumps({k: round(v, 3) for k, v in best.items()}), 'IoU', round(s, 4))
    json.dump(best, open(sys.argv[1], 'w'))
