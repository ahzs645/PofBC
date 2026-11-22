"""Fit circular (or oval) badge lettering with a typeface, letter by letter.

Each letter of the printed illustration is a connected component in the lettering band.
For a candidate font the glyph is scaled (one size and one width factor per run, shared by
all its letters), rotated to the tangent at the component's angle, and placed by centroid
alignment then a small search over rotation (+-4 deg) and translation (0.25 px steps).
The output keeps the font's own outlines under a rigid transform per letter.
"""
import math
import numpy as np, cv2
from fontpaths import *


def letter_components(letters_mask, min_area=25):
    n, lab, st, cen = cv2.connectedComponentsWithStats(letters_mask.astype(np.uint8), connectivity=8)
    return [(i, st[i], cen[i]) for i in range(1, n) if st[i][4] >= min_area], lab


def order_run(comps, centre, start_deg, clockwise=True):
    """sort components by angle from start (screen coords, degrees, 0 = +x, 90 = down)."""
    def key(c):
        a = math.degrees(math.atan2(c[2][1] - centre[1], c[2][0] - centre[0]))
        d = (a - start_deg) % 360 if clockwise else (start_deg - a) % 360
        return d
    return sorted(comps, key=key)


def glyph_polys(font, ch, size, xs, rot_deg, steps=8):
    upm = font['head'].unitsPerEm
    rec, adv = glyph_record(font, ch)
    T0 = glyph_T(size, upm, 0, 0, 0, xs)
    polys = record_to_polys(rec, T0, steps)
    pts = np.concatenate([np.array(p) for p in polys])
    # rotate about the glyph's bbox centre
    cx, cy = (pts.min(0) + pts.max(0)) / 2
    T = Affine.rotate(rot_deg) @ Affine.translate(-cx, -cy) @ T0
    return rec, T


def place_letter(font, ch, size, xs, rot, target, x0, y0, search_rot=4.0):
    """target: binary crop; (x0, y0) its origin. Returns (iou, T_full, rec)."""
    best = None
    tys, txs = np.nonzero(target)
    tcx, tcy = txs.mean() + 0.5, tys.mean() + 0.5
    for drot in np.arange(-search_rot, search_rot + 0.01, 1.0):
        rec, T = glyph_polys(font, ch, size, xs, rot + drot)
        polys = record_to_polys(rec, T, 8)
        # centroid of rendered glyph at origin
        pts = np.concatenate([np.array(p) for p in polys]); mn = pts.min(0) - 2
        tmp = raster([[[(px - mn[0], py - mn[1]) for px, py in pl] for pl in polys]],
                     (int(pts[:, 1].max() - mn[1]) + 3, int(pts[:, 0].max() - mn[0]) + 3))
        gy, gx = np.nonzero(tmp)
        if len(gx) == 0: continue
        gcx, gcy = gx.mean() + 0.5 + mn[0], gy.mean() + 0.5 + mn[1]
        dx, dy = tcx - gcx, tcy - gcy
        def sc(dx, dy):
            sh = [[(px + dx, py + dy) for px, py in pl] for pl in polys]
            return iou(raster([sh], target.shape), target)
        cur = (sc(dx, dy), dx, dy)
        for step in (1.0, 0.5, 0.25):
            imp = True
            while imp:
                imp = False
                for ddx, ddy in ((step, 0), (-step, 0), (0, step), (0, -step)):
                    s = sc(cur[1] + ddx, cur[2] + ddy)
                    if s > cur[0] + 1e-9:
                        cur = (s, cur[1] + ddx, cur[2] + ddy); imp = True
        if best is None or cur[0] > best[0]:
            best = (cur[0], Affine.translate(cur[1] + x0, cur[2] + y0) @ T, rec, rot + drot)
    return best


def fit_run(font, text, comps, lab, centre, size, xs, outward_up=True, pad=4, search_rot=4.0, axes=None):
    """text letters (no spaces) matched in order to comps; returns list of placements."""
    out = []
    assert len(text) == len(comps), (text, len(comps))
    for ch, (i, s, c) in zip(text, comps):
        x, y, w, h, a = s
        x0, y0 = x - pad, y - pad
        target = (lab[y0:y + h + pad, x0:x + w + pad] == i).astype(np.uint8)
        if axes:  # oval badge: outward normal of the ellipse through this point
            a, bb = axes
            ang = math.degrees(math.atan2((c[1] - centre[1]) / bb ** 2, (c[0] - centre[0]) / a ** 2))
        else:
            ang = math.degrees(math.atan2(c[1] - centre[1], c[0] - centre[0]))
        rot = ang + 90 if outward_up else ang - 90
        r = place_letter(font, ch, size, xs, rot, target, x0, y0, search_rot)
        out.append(dict(ch=ch, iou=float(r[0]), T=r[1], rec=r[2], rot=float(r[3])))
    return out


def search_size(font, text, comps, lab, centre, outward_up, sizes, xss, sample=None, axes=None):
    best = None
    idx = sample or list(range(len(text)))
    for size in sizes:
        for xs in xss:
            sub = fit_run(font, ''.join(text[k] for k in idx), [comps[k] for k in idx], lab, centre, size, xs, outward_up, search_rot=2.0, axes=axes)
            m = float(np.mean([p['iou'] for p in sub]))
            if best is None or m > best[0]:
                best = (m, size, xs)
    return best


def run_svg(placements, fill):
    return '<path fill="%s" d="%s"/>' % (fill, ''.join(record_to_svg(p['rec'], p['T']) for p in placements))
