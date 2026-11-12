"""Hand-drawn display lettering reconstructed from the supplied 644 x 468 raster.

No autotracing, bitmap conversion, or third-party font is used. Each reusable
letter is drawn with deliberate straight segments and cubic Bezier curves.
Measurements below position the ink, but do not determine its path geometry.
"""
from pathlib import Path
from xml.sax.saxutils import escape
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

OUT=Path(__file__).resolve().parent
INK='#F9FAE4'
# Cap-height 100, lowercase x-height 70, slightly flared vertical stems.
GLYPHS={
'B':'''M0 0 H28 C47 0 53 7 53 23 V30 C53 40 49 45 39 48 C53 50 58 58 58 71 V79 C58 95 50 100 31 100 H0 L1.2 93 V7 Z M15 7 V46 H27 C38 46 41 41 41 30 V23 C41 11 37 7 27 7 Z M15 53 V93 H30 C42 93 45 88 45 79 V71 C45 59 42 53 30 53 Z''',
'R':'''M0 0 H29 C49 0 56 7 56 22 V31 C56 44 49 49 37 52 L59 95 L63 100 H46 L26 54 H15 V93 L16.2 100 H0 L1.2 93 V7 Z M15 7 V47 H28 C40 47 43 41 43 31 V22 C43 11 39 7 28 7 Z''',
'I':'''M0 0 H18 L17 7 V93 L18 100 H0 L1 93 V7 Z''',
'T':'''M0 0 H58 L57 9 L48 7 H36 V93 L38 100 H20 L22 93 V7 H10 L0 9 Z''',
'S':'''M50 2 L49 11 C40 8 34 7 26 7 C13 7 10 12 10 24 C10 35 15 40 29 46 C48 54 55 62 55 78 C55 96 45 101 27 101 C16 101 9 100 2 98 L2 89 C10 92 17 94 27 94 C39 94 43 90 43 78 C43 66 39 62 24 55 C7 47 0 40 0 25 C0 8 9 0 26 0 C36 0 43 0 50 2 Z''',
'H':'''M0 0 H17 L15 7 V45 H44 V7 L42 0 H59 L57 7 V93 L59 100 H42 L44 93 V53 H15 V93 L17 100 H0 L2 93 V7 Z''',
'C':'''M53 3 L51 12 C44 9 38 7 30 7 C16 7 13 17 13 49 C13 83 17 93 31 93 C39 93 46 91 53 88 L53 98 C46 100 39 101 30 101 C8 101 0 88 0 50 C0 12 8 0 30 0 C39 0 47 1 53 3 Z''',
'O':'''M30 0 C53 0 61 9 61 30 V71 C61 93 53 101 30 101 C8 101 0 93 0 71 V30 C0 9 8 0 30 0 Z M30 7 C16 7 13 14 13 30 V71 C13 88 16 94 30 94 C45 94 48 88 48 71 V30 C48 14 45 7 30 7 Z''',
'L':'''M0 0 H17 L15 7 V92 H41 L51 89 L50 100 H0 L2 93 V7 Z''',
'U':'''M0 0 H17 L15.8 7 V78 C15.8 91 19 94 30 94 C41 94 44 91 44 78 V7 L42.8 0 H59 L57.8 7 V78 C57.8 96 49 101 30 101 C10 101 1.2 96 1.2 78 V7 Z''',
'M':'''M0 0 H19 L43 80 L67 0 H86 L84 7 V93 L86 100 H69 L71 93 V17 L46 100 H36 L10 17 V93 L12 100 H0 L2 93 V7 Z''',
'A':'''M26 0 H40 L66 95 L69 100 H51 L52 94 L45 69 H17 L11 94 L12 100 H0 L3 95 Z M30 13 L19 61 H43 Z''',
'V':'''M0 0 H19 L18 6 L41 86 L63 6 L62 0 H74 L71 7 L45 100 H32 L4 7 Z''',
'E':'''M0 0 H49 L48 10 L41 7 H15 V44 H40 L46 42 V53 L40 51 H15 V93 H43 L53 90 L52 100 H0 L2 93 V7 Z''',
'N':'''M0 0 H18 L52 79 V7 L50 0 H62 L60 7 V100 H47 L10 16 V93 L12 100 H0 L2 93 V7 Z''',
'D':'''M0 0 H27 C51 0 61 11 61 32 V68 C61 90 51 100 27 100 H0 L1.2 93 V7 Z M15 7 V93 H26 C43 93 48 85 48 68 V32 C48 15 43 7 26 7 Z''',
'Y':'''M0 0 H18 L17 6 L37 47 L55 6 L54 0 H66 L63 7 L42 56 V93 L44 100 H26 L28 93 V56 L4 7 Z''',
# Lowercase uses a lighter stem to preserve its size in the small second title.
'e':'''M43 64 H11 V75 C11 89 15 94 28 94 C34 94 39 93 43 90 V98 C38 100 32 101 26 101 C7 101 0 93 0 74 V55 C0 37 7 29 23 29 C39 29 43 37 43 55 Z M11 57 H33 V53 C33 40 31 35 23 35 C15 35 11 40 11 53 Z''',
'p':'''M0 30 H10 L11 34 C16 31 22 29 28 29 C43 29 48 39 48 64 C48 91 42 101 27 101 C21 101 16 99 12 97 V116 L14 122 H0 L2 116 V37 Z M12 41 V90 C16 93 20 94 25 94 C34 94 37 87 37 65 C37 43 34 36 25 36 C20 36 16 38 12 41 Z''',
'a':'''M4 31 C10 30 16 29 24 29 C40 29 45 34 45 48 V93 L47 100 H36 L35 96 C30 99 23 101 17 101 C5 101 0 94 0 80 C0 65 7 58 22 58 H35 V48 C35 38 31 35 22 35 C16 35 10 37 4 39 Z M35 65 H24 C14 65 10 69 10 80 C10 91 13 95 21 95 C27 95 31 93 35 89 Z''',
'r':'''M0 30 H11 L12 35 C17 31 22 29 29 29 V38 C22 36 17 37 12 41 V93 L14 100 H0 L2 93 V37 Z''',
'n':'''M0 30 H11 L12 34 C19 31 24 29 30 29 C43 29 47 35 47 49 V93 L49 100 H35 L37 93 V49 C37 39 34 36 27 36 C22 36 17 37 12 40 V93 L14 100 H0 L2 93 V37 Z''',
'm':'''M0 30 H11 L12 34 C18 31 24 29 30 29 C37 29 41 31 44 35 C50 31 57 29 64 29 C77 29 81 35 81 49 V93 L83 100 H69 L71 93 V49 C71 39 68 36 61 36 C56 36 51 38 47 41 V93 L49 100 H35 L37 93 V49 C37 39 34 36 27 36 C22 36 17 37 12 40 V93 L14 100 H0 L2 93 V37 Z''',
'o':'''M24 29 C42 29 48 37 48 55 V75 C48 93 42 101 24 101 C6 101 0 93 0 75 V55 C0 37 6 29 24 29 Z M24 35 C14 35 11 41 11 55 V75 C11 89 14 95 24 95 C34 95 37 89 37 75 V55 C37 41 34 35 24 35 Z''',
't':'''M10 15 H22 L20 22 V31 H34 V37 H20 V82 C20 91 23 94 30 94 H36 V100 C32 101 29 101 25 101 C14 101 10 95 10 83 V37 H0 V31 H10 Z''',
'f':'''M10 31 V19 C10 4 16 0 28 0 C32 0 36 0 40 1 V8 C36 7 33 6 30 6 C23 6 20 10 20 19 V31 H35 V38 H20 V93 L22 100 H8 L10 93 V38 H0 V31 Z''',
}

# Per-character ink bounds measured to place reconstructed letters accurately.
# These measurements are NOT bitmap contours. Curves above are authored directly.
LINES=[
 ('british','BRITISH',50,46.5,[(137.5,169),(167.8,201),(200.6,214),(212.2,237.8),(242,255.5),(255.1,283),(282.8,315)]),
 ('columbia','COLUMBIA',105.9,46.6,[(164,190.9),(189.5,221.5),(222.5,248),(245.6,275.4),(278.4,319.6),(320.6,351.9),(352.7,365.7),(371.4,399.5)]),
 ('department','Departmentof',327.3,32.4,[(268.1,289.4),(292.7,307.7),(310.3,327),(329.4,343.7),(346.1,357.3),(359.7,371.7),(372.4,402.0),(404.2,420),(422.5,440.6),(442.6,454.4),(468,484),(484,494)]),
 ('travel-industry','TRAVELINDUSTRY',372.0,32.1,[(280,296.9),(300.2,322),(326.4,346.2),(344.8,363.5),(367.0,385),(386.7,404),(416.7,425.3),(428,451),(451.9,474),(475.7,497),(498.6,518),(516.7,533),(535.1,557.8),(556.9,575.7)]),
]

def bounds(path,matrix=None):
 p=BoundsPen(None)
 if matrix: parse_path(path,TransformPen(p,matrix))
 else: parse_path(path,p)
 return p.bounds

def letter(ch,x1,x2,y,h,line,i):
 p=GLYPHS[ch]
 sy=h/100
 # Lowercase metrics are based on the same capital height; real glyph extends
 # naturally above or below the x-height.
 shear=.14
 lo,hi=.001,2
 for _ in range(60):
  sx=(lo+hi)/2
  b=bounds(p,(sx,0,shear*sy,sy,0,y))
  if b[2]-b[0] < x2-x1:lo=sx
  else:hi=sx
 sx=(lo+hi)/2
 b=bounds(p,(sx,0,shear*sy,sy,0,y))
 tx=x1-b[0]
 stroke_width = 1.3 if line in ("british","columbia") else (1.4 if line=="travel-industry" else 0.75)
 return f'<path id="{line}-{i+1:02d}-{ch}" d="{p}" stroke="{INK}" stroke-width="{stroke_width}" stroke-linejoin="round" transform="matrix({sx:.7f} 0 {shear*sy:.7f} {sy:.7f} {tx:.7f} {y:.7f})"/>'

def build():
 out=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 644 468" width="644" height="468">', '<title>Reconstructed British Columbia Department of Travel Industry lettering</title>', '<desc>Hand-authored glyph outlines with original line placement; font-free editable paths.</desc>', f'<g id="lettering" fill="{INK}" fill-rule="evenodd">']
 for name,word,y,h,boxes in LINES:
  assert len(word)==len(boxes),(name,len(word),len(boxes))
  label={'british':'BRITISH','columbia':'COLUMBIA','department':'Department of','travel-industry':'TRAVEL INDUSTRY'}[name]
  out.append(f'<g id="{name}" aria-label="{escape(label)}">')
  for i,(ch,(x1,x2)) in enumerate(zip(word,boxes)):
   out.append(letter(ch,x1,x2,y,h,name,i))
  out.append('</g>')
 out+=['</g>','</svg>']
 (OUT/'lettering.svg').write_text('\n'.join(out))

if __name__=='__main__':build()
