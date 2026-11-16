"""Small helpers: mask a scan, rasterize polygons, coordinate-descent fit by IoU."""
import numpy as np
from PIL import Image, ImageDraw
def mask_of(path, thr=128, crop=None):
    im = Image.open(path).convert('L')
    if crop: im = im.crop(crop)
    return (np.array(im) < thr)
def raster(polys, size, ss=4):
    W, H = size
    im = Image.new('L', (W*ss, H*ss), 0); d = ImageDraw.Draw(im)
    for p in polys: d.polygon([(x*ss, y*ss) for x, y in p], fill=255)
    return np.array(im.resize((W, H), Image.BOX)) > 127
def iou(a, b): return (a & b).sum() / max(1, (a | b).sum())
def fit(model, p0, steps, target, rounds=6, size=None):
    size = size or (target.shape[1], target.shape[0])
    best = dict(p0); bs = iou(raster(model(best), size), target)
    steps = dict(steps)
    for _ in range(rounds):
        improved = True
        while improved:
            improved = False
            for k in steps:
                for d in (-1, 1):
                    t = dict(best); t[k] += d*steps[k]
                    s = iou(raster(model(t), size), target)
                    if s > bs: best, bs, improved = t, s, True
        steps = {k: v/2 for k, v in steps.items()}
    return best, bs
def overlay_sheet(src_path, fitted_mask, out, thr=140, H=260, crop=None):
    """source scan | colour overlay (grey both, blue scan only, magenta vector only), same coordinates."""
    from PIL import Image
    src = Image.open(src_path).convert('RGB')
    if crop: src = src.crop(crop)
    m = np.array(src.convert('L')) < thr
    ov = np.full(m.shape + (3,), 255, np.uint8)
    ov[m & fitted_mask] = (70, 70, 70); ov[m & ~fitted_mask] = (40, 120, 235); ov[~m & fitted_mask] = (230, 40, 160)
    a = src; b = Image.fromarray(ov)
    s = H / a.height
    a = a.resize((round(a.width*s), H), Image.LANCZOS); b = b.resize((round(b.width*s), H), Image.NEAREST)
    sheet = Image.new('RGB', (a.width*2 + 12, H), (235, 235, 235)); sheet.paste(a, (0, 0)); sheet.paste(b, (a.width + 12, 0))
    sheet.save(out, quality=82)
def svg_mask(svg_path, size, viewbox_to_px):
    """Render an SVG into source pixel space: viewbox_to_px = (scale, dx, dy) mapping svg units -> px."""
    import subprocess, tempfile, os, re
    from PIL import Image
    s, dx, dy = viewbox_to_px
    svg = open(svg_path).read()
    inner = re.sub(r'^<svg[^>]*>', '', svg.strip()); inner = re.sub(r'</svg>$', '', inner)
    W, H = size
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><g transform="translate({dx} {dy}) scale({s})">{inner}</g></svg>'
    fd, tmp = tempfile.mkstemp(suffix='.svg'); os.write(fd, doc.encode()); os.close(fd)
    png = tmp + '.png'
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render.js'), tmp, png, str(W)], check=True)
    im = Image.open(png).convert('L'); os.remove(tmp); os.remove(png)
    return np.array(im) < 200
def raster_eo(polys, size, ss=3):
    """Even-odd rasterization (glyph counters punched out)."""
    W, H = size; acc = np.zeros((H*ss, W*ss), bool)
    for p in polys:
        if len(p) < 3: continue
        im = Image.new('1', (W*ss, H*ss), 0); ImageDraw.Draw(im).polygon([(x*ss, y*ss) for x, y in p], fill=1)
        acc ^= np.array(im)
    return np.array(Image.fromarray(acc.astype(np.uint8)*255).resize((W, H), Image.BOX)) > 127
def fit_text(text, fontfile, target, p0, steps, rounds=5, extra=None, **kw):
    """target: bool mask of the region (already cropped, same coords as p0). p: x, y, size, tracking[, hscale, slant]."""
    from textpath import layout, polys
    H, W = target.shape
    def m(p):
        pl, _ = layout(text, fontfile, p['size'], p['x'], p['y'], p.get('tracking', 0), p.get('hscale', 1), p.get('slant', 0), **kw)
        return raster_eo(polys(pl, fontfile) + (extra(p) if extra else []), (W, H))
    best = dict(p0); bs = iou(m(best), target); st = dict(steps)
    for _ in range(rounds):
        imp = True
        while imp:
            imp = False
            for k in st:
                for d in (-1, 1):
                    t = dict(best); t[k] += d*st[k]; s = iou(m(t), target)
                    if s > bs: best, bs, imp = t, s, True
        st = {k: v/2 for k, v in st.items()}
    return best, bs, m(best)
def init_text(text, fontfile, target, cap_px, baseline, left, right, capref='H', **kw):
    """Initial x, y, size, tracking from cap height and ink extents measured on the scan."""
    from textpath import layout, polys, font
    f = font(fontfile); os2 = f['OS/2']; upm = f['head'].unitsPerEm
    cap = getattr(os2, 'sCapHeight', 0) or 0.72*upm
    size = cap_px / (cap/upm)
    def ink(tr):
        pl, _ = layout(text, fontfile, size, 0, 0, tr, **kw); xs = [x for p in polys(pl, fontfile) for x, y in p]
        return min(xs), max(xs)
    lo, hi = -200.0, 400.0
    for _ in range(40):
        mid = (lo + hi)/2; a, b = ink(mid)
        if b - a < right - left: lo = mid
        else: hi = mid
    a, b = ink(lo)
    return dict(x=left - a, y=baseline, size=size, tracking=lo)
def fit_letters(text, fontfile, target, p, rounds=4, glyph_dx=None):
    """Per-letter refinement: global size/y/hscale plus an x offset per glyph (spacing read off the scan).
    p: dict with x, y, size, tracking, hscale. Returns (p, dxs, iou, mask)."""
    from textpath import layout, polys
    H, W = target.shape
    n = len([c for c in text])
    dx = list(glyph_dx) if glyph_dx else [0.0]*n
    def place(p, dx):
        pl, _ = layout(text, fontfile, p['size'], p['x'], p['y'], p.get('tracking', 0), p.get('hscale', 1), p.get('slant', 0))
        out = []
        for i, (g, tr) in enumerate(pl):
            a, b, c, d, e, f = tr; out.append((g, (a, b, c, d, e + dx[i], f)))
        return out
    def m(p, dx): return raster_eo(polys(place(p, dx), fontfile), (W, H))
    bs = iou(m(p, dx), target)
    gst = dict(size=0.5, y=0.5, hscale=0.03); lst = 1.0
    for _ in range(rounds):
        for k in gst:
            for d in (-1, 1):
                while True:
                    t = dict(p); t[k] += d*gst[k]; s = iou(m(t, dx), target)
                    if s > bs: p, bs = t, s
                    else: break
        for i in range(n):
            for d in (-1, 1):
                while True:
                    t = list(dx); t[i] += d*lst; s = iou(m(p, t), target)
                    if s > bs: dx, bs = t, s
                    else: break
        gst = {k: v/2 for k, v in gst.items()}; lst /= 2
    return p, dx, bs, m(p, dx), place(p, dx)
def raster_prims(prims, size, ss=2):
    """Union of (outer, holes) primitives."""
    W, H = size; acc = np.zeros((H*ss, W*ss), bool)
    for outer, holes in prims:
        im = Image.new('1', (W*ss, H*ss), 0); d = ImageDraw.Draw(im)
        d.polygon([(x*ss, y*ss) for x, y in outer], fill=1)
        for h in holes: d.polygon([(x*ss, y*ss) for x, y in h], fill=0)
        acc |= np.array(im)
    return np.array(Image.fromarray(acc.astype(np.uint8)*255).resize((W, H), Image.BOX)) > 127
def fit_prims(model, p0, steps, target, rounds=5, size=None):
    size = size or (target.shape[1], target.shape[0])
    best = dict(p0); bs = iou(raster_prims(model(best), size), target); st = dict(steps)
    for _ in range(rounds):
        imp = True
        while imp:
            imp = False
            for k in st:
                for d in (-1, 1):
                    t = dict(best); t[k] += d*st[k]; s = iou(raster_prims(model(t), size), target)
                    if s > bs: best, bs, imp = t, s, True
        st = {k: v/2 for k, v in st.items()}
    return best, bs
