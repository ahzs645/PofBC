"""Set a string in a font with HarfBuzz shaping (kerning) and return SVG path data, converted to outlines.
Units: output in font units scaled by size/upm; origin at (0, baseline=0), y down."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
class AbsPen(BasePen):
    def __init__(self,gs):
        super().__init__(gs); self.c=[]
    def f(self,p): return ' '.join(f'{v:.3f}'.rstrip('0').rstrip('.') for v in p)
    def _moveTo(self,p): self.c.append('M '+self.f(p))
    def _lineTo(self,p): self.c.append('L '+self.f(p))
    def _qCurveToOne(self,p1,p2): self.c.append('Q '+self.f(p1)+' '+self.f(p2))
    def _curveToOne(self,p1,p2,p3): self.c.append('C '+self.f(p1)+' '+self.f(p2)+' '+self.f(p3))
    def _closePath(self): self.c.append('Z')
    def getCommands(self): return ' '.join(self.c)
from fontTools.pens.transformPen import TransformPen
_cache={}
def text_d(fontfile, text, size=100.0, tracking=0.0, dx=0.0, dy=0.0):
    if fontfile not in _cache:
        data=open(fontfile,'rb').read()
        _cache[fontfile]=(TTFont(fontfile), hb.Font(hb.Face(data)))
    tt,hfont=_cache[fontfile]
    upm=tt['head'].unitsPerEm
    buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hfont,buf,{'kern':True,'liga':False})
    gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
    k=size/upm; x=0.0; ds=[]
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        name=order[info.codepoint]
        pen=AbsPen(gs)
        tp=TransformPen(pen,(k,0,0,-k,dx+x+pos.x_offset*k,dy-pos.y_offset*k))
        gs[name].draw(tp)
        d=pen.getCommands()
        if d: ds.append(d)
        x+=pos.x_advance*k+tracking
    return ' '.join(ds), x
