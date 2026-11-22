"""Fixed-wording reconstructed vector outlines for the report identity study.

This is not a font and does not use/download any font binary. Glyph paths were
analytically reconstructed from high-resolution official public specimens.
Coordinates are em=1000, baseline y=0, positive y down. The restricted set is
intended for the documented branding wording only.
"""
from pathlib import Path
import json,html
_DATA=None
def data():
 global _DATA
 if _DATA is None:_DATA=json.loads(Path(__file__).with_name('glyph_geometry.json').read_text())
 return _DATA
def _layout(text,tracking=0,word_space=0):
 glyphs=data()['glyphs'];x=0.;items=[];boxes=[]
 for i,c in enumerate(text):
  if c==' ':x+=625+word_space
  else:
   if c not in glyphs:raise ValueError(f'Character {c!r} not in restricted branding outline set')
   g=glyphs[c];items.append((c,x,g));b=g['bbox'];boxes.append((b[0]+x,b[1],b[2]+x,b[3]));x+=g['advance']
  if i<len(text)-1:x+=tracking
 box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)] if boxes else [0,0,0,0]
 return items,x,box
def measure_text(text,font_size=100,tracking=0,word_space=0,horizontal_scale=1):
 """tracking/word_space are additional thousandths of em, not CSS em values."""
 items,adv,b=_layout(text,tracking,word_space);s=font_size/1000
 return {'advance':adv*s*horizontal_scale,'ink_bbox':[b[0]*s*horizontal_scale,b[1]*s,b[2]*s*horizontal_scale,b[3]*s],'cap_height':625*s,'glyphs':len(items)}
def text_group(text,font_size=100,tracking=0,word_space=0,color='#163c36',horizontal_scale=1,x=0,y=0,anchor='start',id=None):
 """Return self-contained SVG group with paths; x/y specify the baseline.

 tracking=-50 means -0.05em. word_space=-220 means extra -0.22em.
 horizontal_scale=0.97 means97%. anchor positions ink start/middle/end.
 """
 items,adv,b=_layout(text,tracking,word_space);s=font_size/1000
 shift={'start':-b[0],'middle':-(b[0]+b[2])/2,'end':-b[2]}.get(anchor)
 if shift is None:raise ValueError('anchor must be start, middle or end')
 ident=f' id="{html.escape(str(id),quote=True)}"' if id else ''
 parts=[f'<g{ident} aria-label="{html.escape(text,quote=True)}" fill="{html.escape(color,quote=True)}" fill-rule="evenodd" transform="translate({x:.6f} {y:.6f}) scale({s*horizontal_scale:.9f} {s:.9f}) translate({shift:.6f} 0)">']
 for c,offset,g in items:parts.append(f'<path data-character="{html.escape(c,quote=True)}" transform="translate({offset:.6f} 0)" d="{g["path"]}"/>')
 parts.append('</g>');return ''.join(parts)
def svg_text(text,**kwargs):
 m=measure_text(text,**{k:v for k,v in kwargs.items() if k in ['font_size','tracking','word_space','horizontal_scale']});b=m['ink_bbox'];pad=5
 g=text_group(text,x=pad,y=pad-b[1],**kwargs)
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {b[2]-b[0]+2*pad:.6f} {b[3]-b[1]+2*pad:.6f}">{g}</svg>'
