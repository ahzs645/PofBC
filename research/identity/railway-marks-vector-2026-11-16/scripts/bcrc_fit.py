"""Fit the BCRC acrostic (bcrco.com website logo) with candidate typefaces.

The 485 x 250 site logo (2022 capture of the same artwork as the current 236 x 124 file)
separates into exactly 29 letter components. For a candidate font, one size, one
horizontal scale and one added slant are shared by all 29 letters; each letter is then
placed by translation only (centroid alignment + 0.25 px search). Score: mean per-letter
IoU and whole-mark IoU. Glyph outlines are the font's own, affinely transformed.

usage: bcrc_fit.py red.npy blue.npy candidates.json [out.json]
"""
import sys, json, itertools
import numpy as np, cv2
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from fontpaths import *

TEXT = 'BRITISHCOLUMBIARAILWAYCOMPANY'
red = np.load(sys.argv[1]); blue = np.load(sys.argv[2])
mask = (red | blue).astype(np.uint8)
H, W = mask.shape
n, lab, st, cen = cv2.connectedComponentsWithStats(mask, connectivity=8)
comps = [i for i in range(1, n) if st[i][4] > 30]
comps.sort(key=lambda i: (st[i][1] // 60, st[i][0]))
assert len(comps) == 29
PAD = 6


def letter_target(k):
    i = comps[k]; x, y, w, h, _ = st[i]
    x0, y0 = x - PAD, y - PAD
    t = (lab[y0:y + h + PAD, x0:x + w + PAD] == i).astype(np.uint8)
    return t, x0, y0


def glyph_mask(polys, shape, dx, dy):
    sh = [[(px + dx, py + dy) for px, py in pl] for pl in polys]
    return raster([sh], shape)


def fit_letter(font, ch, size, xs, sk, k, fine=True):
    upm = font['head'].unitsPerEm
    rec, adv = glyph_record(font, ch)
    T = glyph_T(size, upm, 0, 0, slant=sk, xscale=xs)
    polys = record_to_polys(rec, T, steps=8)
    t, x0, y0 = letter_target(k)
    pts = np.concatenate([np.array(p) for p in polys])
    # centroid of rendered glyph at origin (rasterise on a temp canvas)
    minx, miny = pts.min(0); maxx, maxy = pts.max(0)
    tmp = glyph_mask(polys, (int(maxy - miny) + 4, int(maxx - minx) + 4), -minx + 2, -miny + 2)
    ys, xs_ = np.nonzero(tmp)
    gcx, gcy = xs_.mean() + minx - 2, ys.mean() + miny - 2
    ty, tx = np.nonzero(t)
    dx, dy = tx.mean() - gcx, ty.mean() - gcy
    best = (iou(glyph_mask(polys, t.shape, dx, dy), t), dx, dy)
    if fine:
        for step in (1.0, 0.5, 0.25):
            improved = True
            while improved:
                improved = False
                for ddx, ddy in [(step, 0), (-step, 0), (0, step), (0, -step)]:
                    s = iou(glyph_mask(polys, t.shape, best[1] + ddx, best[2] + ddy), t)
                    if s > best[0] + 1e-9:
                        best = (s, best[1] + ddx, best[2] + ddy); improved = True
    return best[0], best[1] + x0, best[2] + y0, rec


def score(font, size, xs, sk, fine=False, ks=range(29)):
    r = [fit_letter(font, TEXT[k], size, xs, sk, k, fine) for k in ks]
    return float(np.mean([x[0] for x in r])), r


def search(font):
    upm = font['head'].unitsPerEm; cap = getattr(font['OS/2'], 'sCapHeight', 0) or 0.72 * upm
    size0 = 54.5 / cap * upm
    best = None
    sample = [0, 3, 8, 12, 19, 24, 27]  # B T C U W O N: varied widths
    for sz in np.linspace(size0 * 0.96, size0 * 1.04, 5):
        for xs in (0.9, 1.0, 1.1, 1.2, 1.3, 1.4):
            for sk in (-2, 1, 4, 7, 10):
                s, _ = score(font, sz, xs, sk, False, sample)
                if best is None or s > best[0]:
                    best = (s, sz, xs, sk)
    # local refinement
    s0, sz, xs, sk = best
    for d_sz, d_xs, d_sk in [(size0 * 0.01, 0.025, 1.0), (size0 * 0.004, 0.01, 0.4)]:
        for a, b, c in itertools.product((-1, 0, 1), repeat=3):
            s, _ = score(font, sz + a * d_sz, xs + b * d_xs, sk + c * d_sk, False, sample)
            if s > best[0]:
                best = (s, sz + a * d_sz, xs + b * d_xs, sk + c * d_sk)
        s0, sz, xs, sk = best
    s, r = score(font, sz, xs, sk, True)
    # whole-mark IoU
    upm = font['head'].unitsPerEm
    allp = []
    for k, (sc, dx, dy, rec) in enumerate(r):
        allp.append(record_to_polys(rec, Affine.translate(dx, dy) @ glyph_T(sz, upm, 0, 0, sk, xs), 8))
    whole = iou(raster(allp, (H, W)), mask)
    return dict(meanLetterIoU=s, wholeIoU=float(whole), size=float(sz), xscale=float(xs), addedSlant=float(sk),
                letters=[dict(ch=TEXT[k], iou=float(x[0]), dx=float(x[1]), dy=float(x[2])) for k, x in enumerate(r)])


if __name__ == '__main__':
    cands = json.load(open(sys.argv[3]))
    results = []
    for fp, axes in cands:
        font = load_font(fp, axes)
        r = search(font); r['font'] = fp.rsplit('/', 1)[-1]; r['fontPath'] = fp; r['axes'] = axes
        results.append(r)
        print(r['font'], axes, 'mean', round(r['meanLetterIoU'], 4), 'whole', round(r['wholeIoU'], 4),
              'size', round(r['size'], 2), 'xs', round(r['xscale'], 3), 'sk', round(r['addedSlant'], 2), flush=True)
    if len(sys.argv) > 4:
        json.dump(results, open(sys.argv[4], 'w'), indent=1)
