"""Outline a line of text from a font file into SVG path data (fontTools), with tracking,
optional horizontal scale and slant. Also returns polygons for raster fitting."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
_cache = {}
def font(path):
    if path not in _cache: _cache[path] = TTFont(path)
    return _cache[path]
class PolyPen(BasePen):
    def __init__(self, gs): super().__init__(gs); self.polys = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i/8; mt = 1-t
            self.cur.append((mt**3*p0[0]+3*mt*mt*t*a[0]+3*mt*t*t*b[0]+t**3*c[0], mt**3*p0[1]+3*mt*mt*t*a[1]+3*mt*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(self, a, b):
        p0 = self.cur[-1]
        for i in range(1, 7):
            t = i/6; mt = 1-t
            self.cur.append((mt*mt*p0[0]+2*mt*t*a[0]+t*t*b[0], mt*mt*p0[1]+2*mt*t*a[1]+t*t*b[1]))
    def _closePath(self): self.polys.append(self.cur); self.cur = []
    _endPath = _closePath
def layout(text, fontfile, size, x, y, tracking=0.0, hscale=1.0, slant=0.0, kern=True, spaces=None):
    """Returns list of (glyphname, transform) placements. tracking in em/1000. y = baseline."""
    f = font(fontfile); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm; hmtx = f['hmtx']
    s = size/upm; pen_x = 0.0; out = []
    kp = {}
    if kern and 'kern' in f:
        for t in f['kern'].kernTables: kp.update(t.kernTable)
    gpos_pairs = _gpos_pairs(f) if kern else {}
    prev = None
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None: continue
        if prev is not None:
            pen_x += kp.get((prev, g), 0) + gpos_pairs.get((prev, g), 0)
        out.append((g, pen_x))
        adv = hmtx[g][0]
        if ch == ' ' and spaces is not None: adv = spaces
        pen_x += adv + tracking*upm/1000
        prev = g
    placements = [(g, (s*hscale, 0, -s*slant, -s, x + px*s*hscale, y)) for g, px in out]
    return placements, pen_x*s*hscale
def _gpos_pairs(f):
    key = id(f)
    if ('gp', key) in _cache: return _cache[('gp', key)]
    pairs = {}
    try:
        for lk in f['GPOS'].table.LookupList.Lookup:
            if lk.LookupType != 2: continue
            for st in lk.SubTable:
                if st.Format == 1:
                    for i, first in enumerate(st.Coverage.glyphs):
                        for pvr in st.PairSet[i].PairValueRecord:
                            v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                            pairs.setdefault((first, pvr.SecondGlyph), v)
                elif st.Format == 2:
                    c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
                    for first in st.Coverage.glyphs:
                        k1 = c1.get(first, 0)
                        for second, k2 in c2.items():
                            rec = st.Class1Record[k1].Class2Record[k2]
                            v = getattr(rec.Value1, 'XAdvance', 0) if rec.Value1 else 0
                            if v: pairs.setdefault((first, second), v)
    except Exception: pass
    _cache[('gp', key)] = pairs; return pairs
def path_d(placements, fontfile, prec=2):
    f = font(fontfile); gs = f.getGlyphSet(); parts = []
    for g, tr in placements:
        pen = SVGPathPen(gs, lambda v: f"{v:.{prec}f}".rstrip('0').rstrip('.'))
        gs[g].draw(TransformPen(pen, tr)); parts.append(pen.getCommands())
    return ''.join(parts)
def glyph_ds(placements, fontfile, prec=2):
    f = font(fontfile); gs = f.getGlyphSet(); out = []
    for g, tr in placements:
        pen = SVGPathPen(gs, lambda v: f"{v:.{prec}f}".rstrip('0').rstrip('.'))
        gs[g].draw(TransformPen(pen, tr)); d = pen.getCommands()
        if d: out.append((g, d))
    return out
def polys(placements, fontfile):
    f = font(fontfile); gs = f.getGlyphSet(); res = []
    for g, tr in placements:
        pp = PolyPen(gs); gs[g].draw(TransformPen(pp, tr)); res.extend(pp.polys)
    return res
