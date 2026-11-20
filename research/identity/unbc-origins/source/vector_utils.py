"""Small vector construction helpers. No bitmap tracing or embedded images.

Type is laid out as font outlines, then individually positioned and optically
fitted. All drawing geometry remains editable in an SVG editor.
"""
from pathlib import Path
from functools import lru_cache
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.areaPen import AreaPen
import re

FONT_ROOT = Path('/usr/share/fonts/opentype/urw-base35')
FONTS = {
    'sans': FONT_ROOT/'NimbusSans-Regular.otf',
    'bold': FONT_ROOT/'NimbusSans-Bold.otf',
    'narrow': FONT_ROOT/'NimbusSansNarrow-Bold.otf',
    'serif': FONT_ROOT/'NimbusRoman-Regular.otf',
    'serif-bold': FONT_ROOT/'NimbusRoman-Bold.otf',
    'italic': FONT_ROOT/'NimbusRoman-Italic.otf',
    'serif-bold-italic': FONT_ROOT/'NimbusRoman-BoldItalic.otf',
    'mono': FONT_ROOT/'NimbusMonoPS-Regular.otf',
}

def num(v):
    return ('%.3f'%float(v)).rstrip('0').rstrip('.') or '0'

@lru_cache(None)
def font_info(name):
    f=TTFont(str(FONTS.get(name,name)))
    gs=f.getGlyphSet(); cm=f.getBestCmap()
    p=BoundsPen(gs); gs[cm[ord('H')]].draw(p)
    return f,gs,cm,p.bounds[3]

def text_paths(text, x, y, height, font='sans', fill='#1D1D1B', width=None,
               align='left', ident='lettering', tracking=0, stroke=None, sw=None, solid_counters=False):
    """Place type by cap top and cap height; width fits ink bounds, not advance.
    Shape dependencies disappear: output contains labelled path glyphs only.
    """
    f,gs,cm,cap=font_info(font)
    items=[]; run=0; bounds=[]
    for i,char in enumerate(text):
        glyph=cm.get(ord(char),'.notdef')
        p=BoundsPen(gs); gs[glyph].draw(p)
        b=p.bounds
        if b:
            items.append((i,char,glyph,run,b))
            bounds.append((run+b[0],b[1],run+b[2],b[3]))
        run += gs[glyph].width + tracking*cap
    if not bounds: return ''
    left=min(b[0] for b in bounds);right=max(b[2] for b in bounds)
    sy=height/cap; sx=(width/(right-left) if width is not None else sy)
    ink_w=(right-left)*sx
    start=x - (ink_w/2 if align=='center' else ink_w if align=='right' else 0)
    attrs=f' fill="{fill}"'
    if stroke: attrs+=f' stroke="{stroke}" stroke-width="{num(sw or 1)}" stroke-linejoin="round" paint-order="stroke fill"'
    lines=[f'<g id="{escape(ident)}" aria-label="{escape(text)}"{attrs}>']
    for i,char,glyph,run,b in items:
        if stroke and solid_counters and char in 'OR':
            record=RecordingPen();gs[glyph].draw(record)
            contours=[];one=[]
            for op,args in record.value:
                one.append((op,args))
                if op in ('closePath','endPath'):
                    area=AreaPen(gs);replayRecording(one,area)
                    contours.append((abs(area.value),one));one=[]
            outer=max(contours,key=lambda c:c[0])[1]
            backing=SVGPathPen(gs,ntos=num)
            replayRecording(outer,TransformPen(backing,(sx,0,0,-sy,start+(run-left)*sx,y+height)))
            lines.append(f'<path id="{escape(ident)}-{i+1:02d}-metal-backing" fill="{stroke}" d="{backing.getCommands()}"/>')
        p=SVGPathPen(gs,ntos=num)
        gs[glyph].draw(TransformPen(p,(sx,0,0,-sy,start+(run-left)*sx,y+height)))
        lines.append(f'<path id="{escape(ident)}-{i+1:02d}-{ord(char)}" d="{p.getCommands()}"/>')
    lines.append('</g>')
    return '\n'.join(lines)

def rect(x,y,w,h,fill,ident='',stroke=None,sw=1):
    attrs=f' fill="{fill}"'+(f' id="{ident}"' if ident else '')
    if stroke: attrs+=f' stroke="{stroke}" stroke-width="{num(sw)}"'
    return f'<path{attrs} d="M{num(x)} {num(y)}H{num(x+w)}V{num(y+h)}H{num(x)}Z"/>'

def rule(x1,y1,x2,y2,color='#1D1D1B',thickness=1):
    return f'<path d="M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}" fill="none" stroke="{color}" stroke-width="{num(thickness)}"/>'

def bar(x,y,right,h,fill,ident,stroke=None,sw=1):
    attrs=f' id="{ident}" fill="{fill}"'
    if stroke: attrs+=f' stroke="{stroke}" stroke-width="{num(sw)}" stroke-linejoin="miter"'
    return f'<path{attrs} d="M{num(x)} {num(y)}H{num(right)}V{num(y+h)}H{num(x+h)}Z"/>'

def svg_doc(w,h,body,title,description,physical=None):
    dims = f'width="{num(w)}" height="{num(h)}"' if physical is None else f'width="{physical[0]}" height="{physical[1]}"'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 {num(w)} {num(h)}" {dims} role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
{body}
</svg>\n'''

def inner_svg(path):
    t=Path(path).read_text()
    t=re.sub(r'<\?xml[^>]*\?>','',t)
    # Inline the actual artwork, not an image link or embedded bitmap.
    t=re.sub(r'^\s*<svg[^>]*>','',t)
    return re.sub(r'</svg>\s*$','',t)

def place_svg(path,x,y,w,h,ident):
    import xml.etree.ElementTree as ET
    root=ET.parse(path).getroot(); vb=[float(x) for x in root.get('viewBox').split()]
    s=min(w/vb[2],h/vb[3]); xx=x+(w-vb[2]*s)/2; yy=y+(h-vb[3]*s)/2
    content=inner_svg(path)
    # Prefix ids so a composite sheet can contain repeated assets safely.
    content=re.sub(r'\bid="([^"]+)"',lambda m:f'id="{ident}-{m.group(1)}"',content)
    content=re.sub(r'url\(#([^\)]+)\)',lambda m:f'url(#{ident}-{m.group(1)})',content)
    content=re.sub(r'(href|xlink:href)="#([^"]+)"',lambda m:f'{m.group(1)}="#{ident}-{m.group(2)}"',content)
    return f'<g id="{ident}" transform="translate({num(xx)} {num(yy)}) scale({num(s)})">{content}</g>'
