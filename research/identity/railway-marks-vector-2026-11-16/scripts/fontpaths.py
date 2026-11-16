"""Shared helpers: font glyph outlines -> affine-transformed SVG paths and polygons.

Glyph outlines come straight from the font files (fontTools); the only changes are
affine transforms (scale, slant, translate, rotate). No live text is emitted.
"""
import math
import numpy as np
import cv2
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.varLib.instancer import instantiateVariableFont

_cache = {}


def load_font(path, axes=None):
    key = (path, tuple(sorted((axes or {}).items())))
    if key not in _cache:
        f = TTFont(path)
        if axes and 'fvar' in f:
            f = instantiateVariableFont(f, axes)
        _cache[key] = f
    return _cache[key]


def glyph_record(font, ch):
    cmap = font.getBestCmap()
    gname = cmap[ord(ch)]
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[gname].draw(pen)
    adv = font['hmtx'][gname][0]
    return pen.value, adv


def kern_pairs(font):
    """Very small GPOS pair-kerning reader (format 1 and 2 PairPos, ValueFormat XAdvance)."""
    pairs = {}
    if 'GPOS' not in font:
        return lambda a, b: 0
    gpos = font['GPOS'].table
    cmap = font.getBestCmap()
    for lookup in gpos.LookupList.Lookup:
        subs = []
        for st in lookup.SubTable:
            if lookup.LookupType == 9:
                st = st.ExtSubTable
            if getattr(st, 'LookupType', lookup.LookupType) == 2 or st.__class__.__name__ == 'PairPos':
                subs.append(st)
        for st in subs:
            if st.Format == 1:
                for i, g1 in enumerate(st.Coverage.glyphs):
                    for pvr in st.PairSet[i].PairValueRecord:
                        v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                        if v:
                            pairs.setdefault((g1, pvr.SecondGlyph), v)
            elif st.Format == 2:
                cd1 = st.ClassDef1.classDefs
                cd2 = st.ClassDef2.classDefs
                for g1 in st.Coverage.glyphs:
                    c1 = cd1.get(g1, 0)
                    rec = st.Class1Record[c1]
                    for g2 in set(cmap.values()):
                        c2 = cd2.get(g2, 0)
                        v = rec.Class2Record[c2].Value1
                        v = getattr(v, 'XAdvance', 0) if v else 0
                        if v:
                            pairs.setdefault((g1, g2), v)
    def k(a, b):
        return pairs.get((cmap.get(ord(a)), cmap.get(ord(b))), 0)
    return k


class Affine:
    """x' = a*x + c*y + e ; y' = b*x + d*y + f"""
    def __init__(self, a=1, b=0, c=0, d=1, e=0, f=0):
        self.m = np.array([[a, c, e], [b, d, f], [0, 0, 1]], float)

    def __matmul__(self, o):
        r = Affine(); r.m = self.m @ o.m; return r

    def apply(self, x, y):
        v = self.m @ np.array([x, y, 1.0])
        return v[0], v[1]

    @staticmethod
    def translate(x, y): return Affine(e=x, f=y)
    @staticmethod
    def scale(sx, sy=None): return Affine(a=sx, d=sx if sy is None else sy)
    @staticmethod
    def rotate(deg):
        t = math.radians(deg); return Affine(math.cos(t), math.sin(t), -math.sin(t), math.cos(t))
    @staticmethod
    def skewx(deg): return Affine(c=math.tan(math.radians(deg)))


def record_to_svg(rec, T, prec=2):
    out = []
    fmt = lambda v: (('%.' + str(prec) + 'f') % v).rstrip('0').rstrip('.')
    pt = lambda p: '%s %s' % tuple(fmt(v) for v in T.apply(*p))
    cur = None
    for op, args in rec:
        if op == 'moveTo':
            out.append('M' + pt(args[0])); cur = args[0]
        elif op == 'lineTo':
            out.append('L' + pt(args[0])); cur = args[0]
        elif op == 'qCurveTo':
            pts = list(args)
            if pts[-1] is None:
                pts = pts[:-1]  # implied on-curve closed contour (rare in TTF here)
            # split implied on-curve points
            for i in range(len(pts) - 1):
                c = pts[i]
                e = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                out.append('Q' + pt(c) + ' ' + pt(e)); cur = e
        elif op == 'curveTo':
            out.append('C' + ' '.join(pt(p) for p in args)); cur = args[-1]
        elif op == 'closePath' or op == 'endPath':
            out.append('Z')
    return ''.join(out)


def record_to_polys(rec, T, steps=12):
    polys = []; poly = []; cur = None
    def q(p0, p1, p2):
        for i in range(1, steps + 1):
            t = i / steps
            yield ((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0], (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])
    def c(p0, p1, p2, p3):
        for i in range(1, steps + 1):
            t = i / steps; s = 1 - t
            yield (s**3*p0[0] + 3*s*s*t*p1[0] + 3*s*t*t*p2[0] + t**3*p3[0], s**3*p0[1] + 3*s*s*t*p1[1] + 3*s*t*t*p2[1] + t**3*p3[1])
    for op, args in rec:
        if op == 'moveTo':
            if poly: polys.append(poly)
            poly = [args[0]]; cur = args[0]
        elif op == 'lineTo':
            poly.append(args[0]); cur = args[0]
        elif op == 'qCurveTo':
            pts = [p for p in args if p is not None]
            for i in range(len(pts) - 1):
                cc = pts[i]
                e = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                poly.extend(q(cur, cc, e)); cur = e
        elif op == 'curveTo':
            poly.extend(c(cur, *args)); cur = args[-1]
        elif op in ('closePath', 'endPath'):
            if poly: polys.append(poly)
            poly = []
    if poly: polys.append(poly)
    return [[T.apply(*p) for p in pl] for pl in polys]


def layout_line(font, text, size, tracking=0.0, kern=True, advances_override=None):
    """Return [(ch, x_offset_in_units_scaled, rec)] for a line set at `size` px per em.
    tracking is in em units."""
    upm = font['head'].unitsPerEm
    s = size / upm
    kf = kern_pairs(font) if kern else (lambda a, b: 0)
    x = 0.0; items = []
    for i, ch in enumerate(text):
        if ch == ' ':
            rec, adv = glyph_record(font, ' ') if ord(' ') in font.getBestCmap() else ([], upm * 0.25)
            x += adv * s + tracking * size
            continue
        rec, adv = glyph_record(font, ch)
        items.append((ch, x, rec, adv * s))
        x += adv * s + tracking * size
        if kern and i + 1 < len(text):
            x += kf(ch, text[i + 1]) * s
    return items, x


def glyph_T(size, upm, x, y, slant=0.0, xscale=1.0):
    """font units (y up) -> canvas (y down) at baseline (x,y)."""
    s = size / upm
    return Affine.translate(x, y) @ Affine.skewx(-slant) @ Affine.scale(s * xscale, -s)


def raster(polys_list, shape):
    """polys_list: list of (polys, fill_value). Even-odd per glyph via XOR."""
    m = np.zeros(shape, np.uint8)
    for polys in polys_list:
        g = np.zeros(shape, np.uint8)
        for pl in polys:
            t = np.zeros(shape, np.uint8)
            cv2.fillPoly(t, [np.round(np.array(pl) * 4).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=2)
            g ^= t
        m |= g
    return m


def iou(a, b):
    a = a.astype(bool); b = b.astype(bool)
    u = (a | b).sum()
    return (a & b).sum() / u if u else 0.0
