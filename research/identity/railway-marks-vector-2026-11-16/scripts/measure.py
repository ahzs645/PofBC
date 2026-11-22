import sys, numpy as np, cv2
from PIL import Image
from scipy.optimize import least_squares
def load(path, thr=128):
    g = np.array(Image.open(path).convert('L'))
    return g, (g < thr).astype(np.uint8)
def comps(b):
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    order = [i for i in np.argsort(-st[:, 4]) if i != 0]
    return lab, st, order
def fit_circle(pts):
    x, y = pts[:, 0], pts[:, 1]
    f = lambda p: np.hypot(x - p[0], y - p[1]) - p[2]
    p0 = [x.mean(), y.mean(), np.hypot(x - x.mean(), y - y.mean()).mean()]
    return least_squares(f, p0).x
def ring_fit(compmask):
    """fit outer and inner edges of a ring component -> (cx, cy, r_out, r_in)"""
    cs, _ = cv2.findContours(compmask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    cs = sorted(cs, key=lambda c: -cv2.contourArea(c))
    o = fit_circle(cs[0][:, 0, :].astype(float) + 0.5)
    i = fit_circle(cs[1][:, 0, :].astype(float) + 0.5)
    return o, i
def fit_line(pts):
    vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01).ravel()
    return np.array([x0, y0]), np.array([vx, vy])
def intersect(l1, l2):
    p, d = l1; q, e = l2
    A = np.array([d, -e]).T; t = np.linalg.solve(A, q - p)
    return p + t[0] * d


def diamond_fit(compmask):
    """outer & inner edge contours of a closed diamond line -> centreline vertices (T,R,B,L), width"""
    cs, _ = cv2.findContours(compmask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    cs = sorted(cs, key=lambda c: -cv2.contourArea(c))
    res = []
    for c in cs[:2]:
        P = c[:, 0, :].astype(float) + 0.5
        cx, cy = P.mean(0)
        ang = np.arctan2(P[:, 1] - cy, P[:, 0] - cx)
        lines = []
        for q in range(4):
            a0 = -np.pi + q * np.pi / 2
            sel = P[(ang > a0 + 0.25) & (ang < a0 + np.pi / 2 - 0.25)]
            lines.append(fit_line(sel))
        V = [intersect(lines[k], lines[(k + 1) % 4]) for k in range(4)]
        res.append(np.array(V))
    O, I = res
    # order of V: quadrant edges starting at angle -pi (upper-left edge ...). Vertex k between edge k and k+1
    ws = []
    for k in range(4):
        a, b = O[k], O[(k + 1) % 4]; d = b - a; n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        ws.append(abs(np.dot(I[k] - a, n)))
    return (O + I) / 2, float(np.mean(ws)), O, I


def radial_ring(b, c, rmin, rmax, n=720):
    """for each angle, outermost black run between rmin and rmax: (r_out, r_in) medians"""
    outs, ins = [], []
    for t in np.linspace(0, 2 * np.pi, n, endpoint=False):
        rs = np.arange(rmax, rmin, -0.25)
        xs = (c[0] + rs * np.cos(t)).astype(int); ys = (c[1] + rs * np.sin(t)).astype(int)
        ok = (xs >= 0) & (ys >= 0) & (xs < b.shape[1]) & (ys < b.shape[0])
        v = np.zeros(len(rs), bool); v[ok] = b[ys[ok], xs[ok]] > 0
        idx = np.where(v)[0]
        if len(idx) == 0: continue
        i0 = idx[0]; i1 = i0
        while i1 + 1 < len(v) and v[i1 + 1]: i1 += 1
        outs.append((t, rs[i0] + 0.5)); ins.append((t, rs[i1] - 0.5))
    return np.array(outs), np.array(ins)


def circle_from_polar(c, arr):
    P = np.stack([c[0] + arr[:, 1] * np.cos(arr[:, 0]), c[1] + arr[:, 1] * np.sin(arr[:, 0])], 1)
    return fit_circle(P)


def chevron_fit(compmask, centre):
    """V-shaped corner piece: returns (end1, vertex, end2, width) along centrelines."""
    from skimage.morphology import skeletonize
    m = compmask.astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    P = cs[0][:, 0, :].astype(float) + 0.5
    # vertex: farthest contour point from centre
    d = np.hypot(P[:, 0] - centre[0], P[:, 1] - centre[1])
    vtx = P[np.argmax(d)]
    sk = skeletonize(m > 0); sy, sx = np.nonzero(sk); S = np.stack([sx, sy], 1).astype(float) + 0.5
    # split skeleton into two arms by side of the line centre->vertex
    v = vtx - centre; n = np.array([-v[1], v[0]])
    side = (S - centre) @ n > 0
    arms = []
    for s in (side, ~side):
        A = S[s]
        dd = np.hypot(A[:, 0] - vtx[0], A[:, 1] - vtx[1])
        A = A[dd > 12]  # avoid the skeleton's corner artefact
        arms.append((fit_line(A), A))
    V = intersect(arms[0][0], arms[1][0])
    ends = []
    for (p, dvec), A in arms:
        t = (A - V) @ dvec
        t_end = t[np.argmax(np.abs(t))]
        ends.append(V + dvec * t_end)
    dt = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    w = 2 * np.median(dt[sk]) - 1
    return ends[0], V, ends[1], float(w)


def radial_transitions(b, c, rmax, rmin, n=720, step=0.25):
    """per angle: radii (scanning inward from rmax) of the first k ink/paper transitions."""
    H, W = b.shape
    out = []
    rs = np.arange(rmax, rmin, -step)
    for t in np.linspace(0, 2 * np.pi, n, endpoint=False):
        xs = (c[0] + rs * np.cos(t)).astype(int); ys = (c[1] + rs * np.sin(t)).astype(int)
        ok = (xs >= 0) & (ys >= 0) & (xs < W) & (ys < H)
        v = np.zeros(len(rs), bool); v[ok] = b[ys[ok], xs[ok]] > 0
        tr = [rs[k] for k in range(1, len(v)) if v[k] != v[k - 1]]
        out.append((t, tr))
    return out


def circles_from_transitions(c, trans, k_list):
    """fit a circle to the k-th transition radius over all angles that have it (robust)."""
    res = {}
    for k in k_list:
        pts = []
        for t, tr in trans:
            if len(tr) > k:
                pts.append((c[0] + tr[k] * np.cos(t), c[1] + tr[k] * np.sin(t)))
        P = np.array(pts)
        cc = fit_circle(P)
        d = np.abs(np.hypot(P[:, 0] - cc[0], P[:, 1] - cc[1]) - cc[2])
        P2 = P[d < max(1.5, np.percentile(d, 70))]
        res[k] = fit_circle(P2)
    return res


def ellipse_ring_edges(b, c, a, bb, s0, s1, maxw=9, n=720, ds=0.0005, want='paper'):
    """find a thin ring (paper run if want='paper', else ink run) between scale factors s0..s1
    of the ellipse (a, bb) about c; returns (outer_pts, inner_pts) edge points."""
    H, W = b.shape
    outs, ins = [], []
    for t in np.linspace(0, 2 * np.pi, n, endpoint=False):
        ss = np.arange(s1, s0, -ds)
        xs = c[0] + ss * a * np.cos(t); ys = c[1] + ss * bb * np.sin(t)
        xi = xs.astype(int).clip(0, W - 1); yi = ys.astype(int).clip(0, H - 1)
        v = b[yi, xi] > 0
        if want == 'paper': v = ~v
        idx = np.where(v)[0]
        if len(idx) == 0: continue
        # runs
        runs = []; st = idx[0]; pr = idx[0]
        for k in idx[1:]:
            if k != pr + 1: runs.append((st, pr)); st = k
            pr = k
        runs.append((st, pr))
        for r0, r1 in runs:
            p0 = np.array([xs[r0], ys[r0]]); p1 = np.array([xs[r1], ys[r1]])
            if 1.5 < np.hypot(*(p0 - p1)) < maxw and r0 > 0 and r1 < len(ss) - 1:
                outs.append(p0); ins.append(p1); break
    return np.array(outs), np.array(ins)


def fit_ellipse_pts(P):
    e = cv2.fitEllipse(P.astype(np.float32))
    (cx, cy), (w, h), ang = e
    return dict(c=[float(cx), float(cy)], axes=[float(w) / 2, float(h) / 2], angle=float(ang))
