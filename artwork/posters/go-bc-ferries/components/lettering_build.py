#!/usr/bin/env python3
"""Build editable SVG lettering from deliberately drawn geometry and saved glyph outlines.

No source image, font installation, contour tracer, or third-party package is
required for this build. The JSON retains independent per-glyph matrices. The
outline geometry is independent of the source image; its placement was measured
against the source. Run: python lettering_build.py [output.svg]
"""
import json,sys,html,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'lettering_geometry.json').read_text())
def build():
 w,h=DATA['canvas'];ink=DATA['colors']['ink'];cream=DATA['colors']['cream'];s=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<title>GO B.C. Ferries — reconstructed vector lettering</title>', '<desc>'+html.escape(DATA['method'])+'</desc>']
 s.append(f'<g id="perimeter-text" fill="{ink}" fill-rule="evenodd">')
 for group in ['perimeter-top','perimeter-bottom']:
  s.append(f'<g id="{group}" aria-label="{html.escape(DATA["groups"][group])}">')
  for g in DATA['glyphs']:
   if g['group']!=group:continue
   m=' '.join(f'{x:.7f}' for x in g['matrix']);extra=''
   if group=='perimeter-bottom' and g['construction'].startswith('font outline'):
    a,b,c,d,_,_=g['matrix'];scale=(math.hypot(a,b)+math.hypot(c,d))/2;extra=f' stroke="{ink}" stroke-width="{.5/scale:.5f}" stroke-linejoin="round"'
   s.append(f'<path id="{g["id"]}" aria-label="{html.escape(g["char"])}" d="{g["path"]}" transform="matrix({m})"{extra}/>')
  s.append('</g>')
 s.append('</g>');s.append(f'<g id="perimeter-dots" fill="{ink}">')
 for i,(cx,cy,r) in enumerate(DATA['perimeter_dots']):s.append(f'<circle id="route-separator-{i+1}" cx="{cx}" cy="{cy}" r="{r}"/>')
 s.append('</g>');s.append(f'<g id="go-bc-ferries" fill="{cream}" fill-rule="evenodd" aria-label="GO B.C. FERRIES">')
 for g in DATA['title_paths']:s.append(f'<path id="title-{g["id"]}" d="{g["path"]}"/>')
 for i,(cx,cy,r) in enumerate(DATA['title_periods']):s.append(f'<circle id="title-period-{i+1}" cx="{cx}" cy="{cy}" r="{r}"/>')
 s.append('</g>');s.append(f'<g id="subtitle" fill="{ink}" fill-rule="evenodd" aria-label="{DATA["groups"]["subtitle"]}">')
 for g in DATA['glyphs']:
  if g['group']!='subtitle':continue
  m=' '.join(f'{x:.7f}' for x in g['matrix']);s.append(f'<path id="{g["id"]}" aria-label="{g["char"]}" d="{g["path"]}" transform="matrix({m})"/>')
 s.append('</g></svg>');return '\n'.join(s)
if __name__=='__main__':
 dest=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'lettering.svg';dest.write_text(build());print(dest)
