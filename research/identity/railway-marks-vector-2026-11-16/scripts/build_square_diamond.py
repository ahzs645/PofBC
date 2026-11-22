"""PGE square diamond (unshaded c.1934; shaded 1935): reconstruction.

Coordinates are source pixels of the registered 300-dpi crops. Fitted geometry:
outer diamond line (least-squares edge lines, both edges), four corner chevrons of the
inner diamond (skeleton line fits per arm), and the ring (circle fits to both edges along
720 radial samples). The interlaced P-G-E monogram is an automatic potrace outline of the
published illustration inside the ring, despeckled (disclosed).

usage: build_square_diamond.py variant(unshaded|shaded) source.png out.svg meta.json
"""
import sys, json
import numpy as np, cv2
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from measure import *
from trace import upsampled_mask, trace_to_path

variant, src, out, meta_out = sys.argv[1:5]
INK = '#1A1A1A'
g, b = load(src)
lab, st, order = comps(b)
H, W = b.shape

# outer diamond = the largest component touching the crop's outer area
outer = order[0] if st[order[0]][2] > 0.8 * W else order[1]
V, w_out, O, I = diamond_fit(lab == outer)
c = V.mean(0)
# chevrons: components whose bbox centre lies on a diagonal axis between ring and outer diamond
chev = []
for i in order:
    x, y, w, h, a = st[i]
    if a < 600 or i == outer: continue
    ccx, ccy = x + w / 2, y + h / 2
    r = np.hypot(ccx - c[0], ccy - c[1])
    if 130 < r < 200 and (min(w, h) < 75) and max(w, h) > 90:
        chev.append(i)
chevrons = [chevron_fit(lab == i, c) for i in chev]
# arm ends: the skeleton extremities (the printed arms taper towards the ring; the
# inner diamond's sides pass just outside it, so they are not extended to meet it)
# ring: outermost dark run inside the chevrons along radial samples (robust median circle)
ringmask = np.zeros_like(b)
for i in order:
    x, y, w, h, a = st[i]
    if i == outer or i in chev: continue
    ringmask |= (lab == i).astype(np.uint8)
o, inn = radial_ring(ringmask, c, 60, 142)
th = o[:, 1] - inn[:, 1]
keep = (th > 5) & (th < 15)
co = circle_from_polar(c, o[keep]); ci = circle_from_polar(c, inn[keep])
rc = ((co[0] + ci[0]) / 2, (co[1] + ci[1]) / 2)
rr, rw = (co[2] + ci[2]) / 2, co[2] - ci[2]




# monogram: inside the ring (minus a margin), traced
yy, xx = np.mgrid[0:H, 0:W]
inside = np.hypot(xx + 0.5 - rc[0], yy + 0.5 - rc[1]) < ci[2] - 1.0
meta = dict(variant=variant, outerDiamond=dict(vertices=V.round(2).tolist(), width=round(w_out, 2)),
            chevrons=[dict(end1=e1.round(2).tolist(), vertex=v.round(2).tolist(), end2=e2.round(2).tolist(), width=round(w, 2)) for e1, v, e2, w in chevrons],
            ring=dict(centre=[round(rc[0], 2), round(rc[1], 2)], radius=round(rr, 2), width=round(rw, 2)))

parts = []
d = 'M%.2f %.2fL%.2f %.2fL%.2f %.2fL%.2f %.2fZ' % tuple(V.ravel())
parts.append('<path fill="none" stroke="%s" stroke-width="%.2f" stroke-linejoin="miter" d="%s"/>' % (INK, w_out, d))
cw = float(np.median([x[3] for x in chevrons]))
chev_d = ''.join('M%.2f %.2fL%.2f %.2fL%.2f %.2f' % (*e1, *v, *e2) for e1, v, e2, w in chevrons)

if variant == 'shaded':
    # Shaded variant: the stippled bands of the illustration (inside the chevrons and in the
    # band between ring and inner circle) are rendered as a flat mid-tone, not as stipple.
    pass

parts.append('<path fill="none" stroke="%s" stroke-width="%.2f" stroke-linejoin="miter" stroke-linecap="butt" d="%s"/>' % (INK, cw, chev_d))
parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" stroke-width="%.2f"/>' % (rc[0], rc[1], rr, INK, rw))
up = 4
m = upsampled_mask(g, inside, up=up, thr=128)
path, n = trace_to_path(m, up=up, turdsize=60, alphamax=1.0, opttolerance=0.2)
parts.append('<path fill="%s" fill-rule="evenodd" d="%s"/>' % (INK, path))
meta['monogramTrace'] = dict(tool='potracer 0.0.4', upsample=up, threshold=128, turdsize=60, alphamax=1.0, opttolerance=0.2, contours=n)

# tight viewBox from outer diamond outer vertices
pad = 0.5
x0, y0 = O[:, 0].min() - pad, O[:, 1].min() - pad
x1, y1 = O[:, 0].max() + pad, O[:, 1].max() + pad
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%.2f" height="%.2f">'
       '<title>Pacific Great Eastern Railway: square diamond monogram</title>%s</svg>\n'
       % (x0, y0, x1 - x0, y1 - y0, x1 - x0, y1 - y0, ''.join(parts)))
open(out, 'w').write(svg)
json.dump(meta, open(meta_out, 'w'), indent=1)
print(json.dumps(meta)[:600])
