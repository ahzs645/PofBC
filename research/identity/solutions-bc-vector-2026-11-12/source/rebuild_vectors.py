"""Rebuild the five SVG versions from manually constructed geometry.

Python standard library only. This program never reads or traces a bitmap.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'geometry.json').read_text())
OUT=HERE.parent/'rebuilt'
OUT.mkdir(exist_ok=True)

def artwork(emblem_colour,letter_colour,include_text=True):
    e=DATA['emblem']
    parts=[f'<g id="emblem" fill="{emblem_colour}">']
    for figure in e['figures']:
        transform=f' transform="{figure["transform"]}"' if figure.get('transform') else ''
        parts.append(f'<path id="{figure["id"]}" d="{e["masters"][figure["master"]]}"{transform}/>')
    for name,x,y,r in e['heads']:
        parts.append(f'<circle id="head-{name}" cx="{x}" cy="{y}" r="{r}"/>')
    parts.append('</g>')
    if include_text:
        t=DATA['lettering']
        for key,gid in [('main','wordmark'),('tagline','tagline')]:
            parts.append(f'<g id="{gid}" fill="{letter_colour}" fill-rule="evenodd">')
            glyphs=t[key+'_glyphs']
            for i,(ch,x,y,sx,sy) in enumerate(t[key+'_positions']):
                parts.append(f'<path id="{gid}-{i+1}-{ch}" data-glyph="{ch}" transform="translate({x} {y}) scale({sx} {sy})" d="{glyphs[ch]}"/>')
            if key=='main':
                parts.append(f'<path id="wordmark-i-dot" d="{t["i_dot"]}"/>')
            parts.append('</g>')
    return '\n'.join(parts)

def document(content,frame,background=None):
    x,y,w,h=frame
    bg=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{background}"/>\n' if background else ''
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}" role="img">
<title>Solutions BC - Shared Services</title>
<desc>Manually reconstructed vector geometry with custom outlined lettering. No bitmap images or external fonts.</desc>
{bg}{content}
</svg>
'''

p=DATA['palette'];f=DATA['frames']
versions=[
    ('solutions-bc-recreated.svg',artwork(p['emblem'],p['lettering']),f['original'],p['background']),
    ('solutions-bc-transparent.svg',artwork(p['emblem'],p['lettering']),f['tight'],None),
    ('solutions-bc-black.svg',artwork('#000000','#000000'),f['tight'],None),
    ('solutions-bc-white.svg',artwork('#FFFFFF','#FFFFFF'),f['tight'],None),
    ('solutions-bc-emblem.svg',artwork(p['emblem'],p['lettering'],False),f['emblem'],None),
]
for name,content,frame,bg in versions:
    (OUT/name).write_text(document(content,frame,bg))
    print(OUT/name)
