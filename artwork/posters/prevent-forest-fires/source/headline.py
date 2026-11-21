"""Constructed display lettering for the BC Forest Service poster.

These seven reusable glyph masters were drawn from typographic structure:
italic stems, curved bowls and counters, flared entrance strokes, and convex
terminal edges. No pixel contours, autotracing, or embedded raster is used.
Coordinates are design units; repeated letters share one master.
"""
from pathlib import Path

INK = '#242332'
IVORY = '#F5F0D7'

# Italic, approximately 180-unit cap height. The slight curvature of top/bottom
# terminals is intentional: the source is display lettering, not obliqued text.
GLYPHS = {
'F': '''M40,7 C77,1 127,2 171,8 L153,46 C126,42 100,42 69,43
L80,48 L67,77 C82,76 98,77 112,79 L98,116 C81,114 67,114 53,116
L31,176 L-15,176 L42,46 L13,47 Z''',
'O': '''M100,0 C137,0 158,19 153,63 C151,111 124,154 80,172
C40,189 0,173 0,136 C0,100 22,44 56,18 C70,7 85,1 100,0 Z
M100,42 C84,43 68,60 58,83 C46,111 40,131 52,136
C65,141 83,127 95,106 C110,81 124,42 100,42 Z''',
'R': '''M49,10 C83,1 130,0 158,12 C181,23 188,47 176,72
C167,97 141,111 125,115 L149,176 C132,173 120,173 107,176
L87,126 L60,126 L50,175 C29,173 16,173 0,176 L52,49 L30,50 Z
M82,48 C109,47 131,47 140,53 C138,65 112,78 80,85 L93,52 Z''',
'E': '''M43,12 C86,5 126,5 166,9 L150,48 C127,46 101,44 70,45
L84,50 L75,70 L118,70 L103,107 C84,106 72,106 60,107
L49,137 C71,140 94,137 121,133 L103,175 C75,180 46,181 19,177
C5,175 0,173 3,160 L45,49 L25,50 Z''',
'S': '''M155,10 L139,49 C115,41 91,46 75,58
C85,72 118,84 129,103 C146,134 115,164 80,175
C52,184 22,180 0,173 L15,132 C43,142 73,134 95,124
C65,111 34,101 33,77 C29,50 49,27 74,16
C99,4 132,1 155,10 Z''',
'T': '''M24,10 C68,5 109,6 151,9 L132,47 C115,45 95,44 76,43
L91,49 L45,178 L0,178 L53,43 C36,42 21,45 3,49 Z''',
'I': '''M70,0 C86,2 101,2 116,1 L46,170 L0,171 Z''',
}

# Optical placements in the fixed 1000 by 1440 design. The common masters
# retain bounded width/height differences between the hand-lettered lines.
LINES = [
 ('FOREST', [
  ('F', 96, 461, 0.929625, 0.995),
  ('O', 216, 461, 1.0, 1.0),
  ('R', 349, 462, 1.02, 1.00495),
  ('E', 520, 462, 1.0, 0.995),
  ('S', 641, 460, 0.995, 1.0),
  ('T', 778, 461, 1.0403, 0.99),
 ]),
 ('FIRES', [
  ('F', 161, 684, 0.9888, 0.98455),
  ('I', 279, 689, 1.0, 0.9849),
  ('R', 360, 684, 0.9999, 0.989473),
  ('E', 524, 684, 1.01, 0.98),
  ('S', 653, 682, 1.025, 0.995),
 ]),
]

# Final uniform six-unit keyline, selected by natural-colour and separate
# ivory-mask review after testing the optically fitted wider alternatives.
OUTLINE_WIDTHS = {
 'FOREST': (6.0, 6.0, 6.0, 6.0, 6.0, 6.0),
 'FIRES': (6.0, 6.0, 6.0, 6.0, 6.0),
}

def build_headline(stroke_width=6):
    bits = ['<g id="headline-lettering" fill="'+INK+'" stroke="'+IVORY+'" stroke-width="'+str(stroke_width)+'" stroke-linejoin="miter" stroke-miterlimit="2.5" fill-rule="evenodd">']
    for word, glyphs in LINES:
        bits.append(f'<g id="word-{word.lower()}" aria-label="{word}">')
        for i,(letter,x,y,sx,sy) in enumerate(glyphs):
            outline = stroke_width * OUTLINE_WIDTHS[word][i] / 6
            bits.append(f'<path id="{word.lower()}-{i+1}-{letter.lower()}" d="{GLYPHS[letter]}" stroke-width="{outline:g}" transform="translate({x} {y}) scale({sx} {sy})"/>')
        bits.append('</g>')
    bits.append('</g>')
    return '\n'.join(bits)

if __name__ == '__main__':
    out=Path(__file__).with_name('headline-preview.svg')
    out.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1440" viewBox="0 0 1000 1440">\n<rect width="1000" height="1440" fill="#F77913"/>\n'+build_headline()+'\n</svg>')
    print(out)
