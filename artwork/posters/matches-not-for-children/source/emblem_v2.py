#!/usr/bin/env python3
"""Seal revision: analytic rings, fitted pre-existing font outlines, drawn tree.

The photo provides landmark and glyph-transform fitting. No source-pixel
contours are used to draw paths. URW Bookman Demi is a fitted substitute;
the historical face has not been identified.
"""
from pathlib import Path
import math,json,os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT=Path(__file__).resolve().parent
INK='#1d2424'
FIT=json.loads((OUT/'letter_transform_fits.json').read_text())['bookman']
FONT=Path(os.environ.get('BCFS_SEAL_FONT',FIT['font'])).expanduser()
if not FONT.is_file():
 raise FileNotFoundError('URW Bookman Demi is required to regenerate the seal outlines. Set BCFS_SEAL_FONT to the installed URWBookman-Demi.otf file; the delivered SVGs themselves need no font installation.')
font=TTFont(FONT);glyphs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm

def ellipse(cx,cy,rx,ry):
 return f'M{cx-rx:.4f},{cy:.4f}a{rx:.4f},{ry:.4f} 0 1 0 {2*rx:.4f},0a{rx:.4f},{ry:.4f} 0 1 0 {-2*rx:.4f},0Z'

def outlined_letters():
 out=[]
 for row in FIT['glyphs']:
  dx,dy,da,sx,sy=row['fit'];th=row['angle']+math.radians(da);u,v=math.cos(th),math.sin(th)
  # Font contours are drawn at 3x poster size, matching the local seal geometry.
  a=row['em']/upm*row['ws']*sx*3;b=row['em']/upm*sy*3
  x=(row['x']+dx-844.5)*3;y=(row['y']+dy-1132.5)*3
  p=SVGPathPen(glyphs);glyphs[cmap[ord(row['ch'])]].draw(TransformPen(p,(a*u,a*v,b*v,-b*u,x,y)))
  out.append(p.getCommands())
 return out

def emblem_group():
 # The outer oval remains fixed. The inner oval is nudged left 0.65 poster unit
 # to follow the photographic registration of its exposed pale field.
 parts=[ellipse(210,255,209,254),ellipse(208.05,262,109,165),
        ellipse(210,255,191,236),ellipse(210,255,186.6,231.6),
        ellipse(208.05,262,119,175),ellipse(208.05,262,114.8,170.8)]
 parts+=outlined_letters()
 tree='M207,99 C205,114 200,126 197,139 L199,144 190,161 192,166 183,184 187,188 179,208 182,211 177,229 180,233 169,253 174,256 167,272 173,275 160,294 157,302 147,311 197,310 197,349 214,349 214,310 269,311 260,300 255,290 248,283 252,279 243,263 247,260 239,246 243,242 233,225 237,221 229,202 232,199 225,182 228,177 219,159 222,154 214,137 C213,123 209,110 207,99Z'
 mountains='M101,292 L119,288 129,290 145,300 154,298 164,305 M266,301 L277,298 287,305 294,302 315,316'
 return f'''<g id="poster-emblem-v2" transform="translate(844.5 1132.5) scale(0.3333333333)" fill="{INK}">
 <defs><clipPath id="poster-emblem-interior-v2"><ellipse cx="208.05" cy="262" rx="109" ry="165"/></clipPath></defs>
 <path id="emblem-rings-and-lettering-v2" fill-rule="evenodd" d="{' '.join(parts)}"/>
 <g id="emblem-scene-v2" clip-path="url(#poster-emblem-interior-v2)">
  <path id="emblem-mountains-v2" d="{mountains}" fill="none" stroke="{INK}" stroke-width="3.3" stroke-linejoin="round"/>
  <path id="emblem-tree-v2" d="{tree}" transform="matrix(1.07702552 0 0 .99246708 -15.6853565 1.783)"/>
  <path id="emblem-water-v2" d="M98,324 H322 M98,331 H322 M98,339 H322" fill="none" stroke="{INK}" stroke-width="3.3"/>
  <path id="emblem-foreground-v2" d="M98,344.5 H322 V440 H98Z"/>
 </g></g>'''

def doc(group,view='0 0 1000 1400',w=1000,h=1400):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{view}"><title>BC Forest Service oval seal - fitted reconstruction revision 2</title><desc>Analytic ellipse rings, URW Bookman Demi letter outlines fitted by glyph transforms, manually authored tree and landscape. Serif face is an approximation, not an identification of the historical typeface. All negative lettering and landscape sky areas are transparent.</desc>{group}</svg>'''

if __name__=='__main__':
 group=emblem_group()
 (OUT/'emblem_v2.svg').write_text(doc(group))
 (OUT/'emblem_v2_isolated.svg').write_text(doc(group,'842 1130 145 175',580,700))
 (OUT/'emblem_v2_preview.svg').write_text(doc('<rect x="837" y="1125" width="155" height="190" fill="#e8ad55"/>'+group,'837 1125 155 190',465,570))
