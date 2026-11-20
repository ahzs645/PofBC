#!/usr/bin/env python3
"""Construct the decal's condensed lettering from a small, hand-drawn glyph set.

No contours are extracted from the source raster. Each master is described by
straight segments, deliberately chosen cubic curves, and small corner rounds.
Measured source bounds are used for placement and width/height only.

The source is hand lettered or optically modified display lettering; these
masters do not claim to identify or reproduce a commercially named font.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json
HERE=Path(__file__).resolve().parent
# Each glyph occupies the stated nominal width by 100 design units.
GLYPHS={
 'A': (52, '''M20 0 L31 0 Q33 0 33.6 3 L51.8 96 Q52.6 100 49.3 100 L38.8 100 Q36.3 100 35.8 97 L32.1 81 L18.2 81 L14.9 97 Q14.3 100 11.7 100 L2.8 100 Q-.5 100 .2 96 L17.3 3 Q17.8 0 20 0 Z M25.3 44 L22.2 64 Q22 66 23.5 66 L27.8 66 Q29.4 66 29 64 Z'''),
 'E': (46, '''M3 0 L43 0 Q46 0 46 3 L46 10 Q46 13.5 43 13.5 L18 13.5 Q15.8 13.5 15.8 16 L15.8 38 Q15.8 40.5 18.3 40.5 L34 40.5 Q37.2 40.5 37.2 43.5 L37.2 51.5 Q37.2 54.8 34 54.8 L18.3 54.8 Q15.8 54.8 15.8 57.3 L15.8 84 Q15.8 87 18.5 87 L43 87 Q46 87 46 90 L46 97 Q46 100 43 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z'''),
 'F': (45, '''M3 0 L42 0 Q45 0 45 3 L45 10 Q45 13.6 42 13.6 L17.3 13.6 Q15 13.6 15 16.2 L15 39 Q15 41.3 17.7 41.3 L34 41.3 Q37 41.3 37 44.3 L37 51.8 Q37 55 34 55 L17.7 55 Q15 55 15 58 L15 97 Q15 100 12 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z'''),
 'I': (14, '''M3 0 L11 0 Q14 0 14 3 L14 97 Q14 100 11 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z'''),
 'L': (42, '''M3 0 L12 0 Q15 0 15 3 L15 84 Q15 87 18 87 L39 87 Q42 87 42 90 L42 97 Q42 100 39 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z'''),
 'N': (48, '''M3 0 L13.7 0 Q16 0 16.7 3 L33.2 53 L33.2 3 Q33.2 0 36.2 0 L45 0 Q48 0 48 3 L48 97 Q48 100 45 100 L34.4 100 Q32.2 100 31.4 97.7 L14.5 47 L14.5 97 Q14.5 100 11.5 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z'''),
 'O': (46, '''M23 0 C7 0 0 8 0 25 L0 75 C0 93 7 100 23 100 C39 100 46 93 46 75 L46 25 C46 8 39 0 23 0 Z M23 14 C29 14 31 18 31 27 L31 73 C31 82 29 86 23 86 C17 86 15 82 15 73 L15 27 C15 18 17 14 23 14 Z'''),
 'P': (48, '''M3 0 L25 0 C41 0 48 8 48 28 C48 48 41 58 16 58 L14 58 L14 97 Q14 100 11 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z M14 14 L14 44 L23 44 C32 44 34 39 34 29 C34 18 32 14 23 14 Z'''),
 'R': (46, '''M3 0 L24 0 C39.5 0 46 8.2 46 27.8 C46 39.5 43.8 46.1 38.7 51.1 C43.7 56.2 45 64 45 77 L45 97 Q45 100 42 100 L33 100 Q30 100 30 97 L30 76 C30 63.2 28 58 21 58 L14 58 L14 97 Q14 100 11 100 L3 100 Q0 100 0 97 L0 3 Q0 0 3 0 Z M14 14 L14 44 L22 44 C29.4 44 31.7 39.4 31.7 28.8 C31.7 18 29 14 22 14 Z'''),
 'S': (46, '''M22.2 0 C37.9 0 45.2 9.7 45.2 27.6 Q45.2 30.5 42.2 30.5 L33.4 30.5 Q30.4 30.5 30.4 27.5 C30.3 17.5 27.9 13.4 22.5 13.4 C17.2 13.4 15.7 17.3 15.7 24.3 C15.7 32.7 24.5 38.1 32.9 47.6 C42.7 59.7 46 68 46 79.8 C46 91 36.3 100 23.5 100 C7 100 0 90.4 0 71.2 Q0 68.2 3 68.2 L11.8 68.2 Q14.8 68.2 14.8 71.2 C14.9 82.9 17.3 87.2 23.3 87.2 C29.2 87.2 31.3 83.8 31.3 77.1 C31.3 69.9 27.7 64.1 18.3 53.5 C7.7 41.7 0 33.7 0 22.4 C0 8.5 8.5 0 22.2 0 Z'''),
 'T': (54, '''M3 0 L51 0 Q54 0 54 3 L54 10 Q54 13 51 13 L34.4 13 Q32 13 32 15.5 L32 97 Q32 100 29 100 L21 100 Q18 100 18 97 L18 15.5 Q18 13 15.6 13 L3 13 Q0 13 0 10 L0 3 Q0 0 3 0 Z'''),
 'U': (48, '''M3 0 L12.5 0 Q15.5 0 15.5 3 L15.5 74 C15.5 83 18.1 86.5 24.1 86.5 C30.2 86.5 32.6 83 32.6 74 L32.6 3 Q32.6 0 35.6 0 L45 0 Q48 0 48 3 L48 75 C48 93 41.1 100 24 100 C7 100 0 93 0 75 L0 3 Q0 0 3 0 Z'''),
 'V': (49, '''M2.1 0 L10.2 0 Q12.7 0 13.1 3 L22.8 69.5 L37.1 3 Q37.7 0 40.1 0 L46.6 0 Q49.5 0 48.9 3 L30.8 97.5 Q30.3 100 27.9 100 L17.6 100 Q15.1 100 14.7 97.5 L.1 3 Q-.4 0 2.1 0 Z'''),
}
# Explicit visual measurements: x, y, width, height. Bounds exclude scan fringe.
TOP=[('E',544,426,45,99),('A',702,430,52,99),('R',759,431,48,99),('E',811,432,46,99),('F',864,432,42,99),('U',910,433,48,102),('L',968,435,42,99)]
LOWER=[('P',54,709,48,98),('R',106,709,45,98),('E',161,710,41,99),('V',212,710,49,99),('E',269,711,43,99),('N',322,711,48,100),('T',377,712,54,100),('F',478,713,44,100),('O',526,711,46,106),('R',580,714,46,101),('E',633,715,44,100),('S',685,714,45,105),('T',737,717,49,100),('F',828,718,41,100),('I',877,719,13,100),('R',902,720,46,100),('E',962,721,42,100),('S',1009,720,45,104)]

def paths_for(entries,prefix):
 out=[]
 for i,(ch,x,y,w,h) in enumerate(entries):
  natural_w,d=GLYPHS[ch]
  # The second T has a narrower crossbar but retains the original stem weight.
  # Apply one explicit optical width variant instead of thinning its stem.
  if ch == 'T' and w < 51:
   d='M3 0 L51 0 Q54 0 54 3 L54 10 Q54 13 51 13 L37 13 Q34.5 13 34.5 15.5 L33 97 Q33 100 30 100 L21 100 Q18 100 18 97 L19 15.5 Q19 13 16.5 13 L3 13 Q0 13 0 10 L0 3 Q0 0 3 0 Z'
  out.append(f'<g id="{prefix}-{i+1:02}-{ch}" aria-label="{ch}"><path d="{d}" transform="translate({x} {y}) scale({w/natural_w:.7f} {h/100:.7f})"/></g>')
 return '\n'.join(out)

header='''<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="1234" height="909" viewBox="0 0 1234 909"><title>Reconstructed condensed lettering — BC Forest Service decal</title><desc>Deliberately drawn reusable glyph masters. The small E, AREFUL and PREVENT FOREST FIRES lettering. No embedded raster or font dependency.</desc>'''
body=f'''<g id="condensed-lettering" fill="#ffffff" fill-rule="evenodd"><g id="be-careful-small-letters">{paths_for(TOP,'upper')}</g><g id="prevent-forest-fires">{paths_for(LOWER,'lower')}</g></g>'''
(HERE/'white_lettering.svg').write_text(header+body+'</svg>')
(HERE/'lettering_preview.svg').write_text(header+'<rect width="1234" height="909" fill="#53594f"/>'+body+'</svg>')
(HERE/'glyph_masters.json').write_text(json.dumps({'construction':'Hand drawn outline masters; no bitmap contour extraction','units_per_cap_height':100,'masters':{k:{'width':v[0],'path':v[1]} for k,v in GLYPHS.items()},'upper_placements':TOP,'lower_placements':LOWER},indent=2))
print('Wrote white_lettering.svg, lettering_preview.svg, glyph_masters.json')
