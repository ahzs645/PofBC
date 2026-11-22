"""Set text in a font and return it as SVG path data (outlines; no live text, no font dependency).

    from outline import Font
    f = Font('EBGaramond[wght].ttf', wght=400)      # or a .pfb / .otf / static .ttf
    d, advance = f.path('BC', size=100, x=0, y=0, tracking=0)   # y is the baseline

Kerning from a TrueType/OpenType 'kern'/GPOS pair table is not applied; spacing is set explicitly
by the caller (tracking and per-pair offsets) to match the source image.
"""
import io
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


class Font:
    def __init__(self, path, wght=None):
        self.file = path
        if path.lower().endswith('.pfb'):
            from fontTools.t1Lib import T1Font
            t1 = T1Font(path); t1.parse()
            self.gs = t1.getGlyphSet()
            self.upm = 1000
            enc = t1.font['Encoding']
            if isinstance(enc, str):
                from fontTools.encodings.StandardEncoding import StandardEncoding
                enc = StandardEncoding
            self.cmap = {}
            for code, name in enumerate(enc):
                if name and name != '.notdef':
                    self.cmap.setdefault(code, name)
            from fontTools.pens.basePen import NullPen
            def adv(g):
                cs = self.gs[g]; cs.draw(NullPen()); return cs.width
            self.adv = adv
        else:
            tt = TTFont(path)
            if wght is not None and 'fvar' in tt:
                from fontTools.varLib.instancer import instantiateVariableFont
                tt = instantiateVariableFont(tt, {'wght': wght})
            self.tt = tt
            self.gs = tt.getGlyphSet()
            self.upm = tt['head'].unitsPerEm
            self.cmap = tt.getBestCmap()
            self.adv = lambda g: tt['hmtx'][g][0]

    def glyph(self, ch):
        return self.cmap[ord(ch)]

    def path(self, text, size, x=0.0, y=0.0, tracking=0.0, kerns=None):
        """tracking: extra space after each glyph, in output units; kerns: {index: extra offset before glyph i}."""
        k = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
        cx = x
        for i, ch in enumerate(text):
            if kerns and i in kerns: cx += kerns[i]
            if ch == ' ':
                cx += self.adv(self.glyph(' ')) * k + tracking; continue
            g = self.glyph(ch)
            tp = TransformPen(pen, (k, 0, 0, -k, cx, y))
            self.gs[g].draw(tp)
            cx += self.adv(g) * k + tracking
        return pen.getCommands(), cx - x
