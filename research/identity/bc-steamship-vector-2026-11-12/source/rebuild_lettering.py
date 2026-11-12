#!/usr/bin/env python3
"""Construct outlined approximation lettering from installed fonts.

This generator reads fonts only, never the reference bitmap. Optical target
widths for the straight company name were manually chosen from the source strip.
The circular inscription is explicitly provisional and is not an original font
identification or an exact reconstruction of the engraved lettering.
"""
from pathlib import Path
import math,json
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE=Path(__file__).resolve().parent
SANS='/usr/share/fonts/opentype/urw-base35/URWGothic-Book.otf'
FRAKTUR='/usr/share/fonts/truetype/lyx/eufm10.ttf'

def load(path):
    f=TTFont(path)
    return f.getGlyphSet(),f.getBestCmap()

def bounds(gs,glyph):
    p=BoundsPen(gs);glyph.draw(p)
    return p.bounds

def path(gs,glyph,transform):
    p=SVGPathPen(gs);glyph.draw(TransformPen(p,transform))
    return p.getCommands()

def document(paths,w,h,title,desc):
    return '\n'.join(['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<title>{title}</title>',f'<desc>{desc}</desc>','<g id="lettering" fill="#000000">',*paths,'</g>','</svg>',''])

# Targets use units of the small source strip. The vector enlarges each unit 10x.
# These widths are regularized optical estimates, not pixel contour traces.
widths={'B':5.8,'R':6.5,'I':.9,'T':4.8,'H':6.0,'S':5.5,'C':7.5,'O':8.9,'L':3.8,'U':6.4,'M':9.5,'A':6.7,'E':4.8,'P':5.7,'N':6.9,'Y':6.5,'D':7.3,'7':5.2,'9':6.1,'1':2.9,'5':5.9,'(':2.9,')':2.9,'.':.9}
words=[('BRITISH',8,50.8),('COLUMBIA',56,119),('STEAMSHIP',127,191.5),('COMPANY',196,258),('(1975)',263.5,301.6),('LTD.',307,328)]
gs,cmap=load(SANS);result=[];letter=0
for word,start,end in words:
    gap=((end-start)-sum(widths[c] for c in word))/(len(word)-1)
    x=start
    for c in word:
        gl=gs[cmap[ord(c)]];x0,y0,x1,y1=bounds(gs,gl)
        sx=widths[c]*10/(x1-x0);sy=100/739
        # Baseline and cap height are fixed; each glyph's ink width is regularized.
        transform=(sx,0,0,-sy,x*10-x0*sx,140)
        result.append(f'<path id="wordmark-letter-{letter:02d}" data-character="{c}" d="{path(gs,gl,transform)}"/>')
        x+=widths[c]+gap;letter+=1
(HERE/'bc-steamship-wordmark-outlined.svg').write_text(document(result,3360,200,'British Columbia Steamship Company (1975) Ltd. — reconstructed company name','Outlined geometric sans-serif approximation using optically adjusted URW Gothic Book letterforms. Source strip is too small to confirm its original font. No live text or embedded raster.'),encoding='utf-8')

# Provisional Euler Fraktur setting. The source inscription is more ornate and
# has different B/C/S/L shapes. Numerals are brought to capital height.
gs,cmap=load(FRAKTUR)
text='British Columbia Steamship Company (1975) Ltd.'
items=[]
for c in text:
    gl=gs[cmap[ord(c)]]
    b=bounds(gs,gl)
    sy=100/1415
    if c.isdigit() and b: sy=100/(b[3]-min(b[1],0))
    items.append((c,gl,b,sy,gl.width*sy))
R=550;start=212;end=509;target=R*math.radians(end-start)
advance=sum(a[4] for a in items);compression=target/advance
result=[];pos=0
for index,(c,gl,b,sy,a) in enumerate(items):
    aa=a*compression
    theta=math.radians(start)+(pos+aa/2)/R
    sn,cs=math.sin(theta),math.cos(theta)
    sx=sy*compression
    if b:
        transform=(sx*cs,sx*sn,sy*sn,-sy*cs,750+R*sn-gl.width/2*sx*cs,750-R*cs-gl.width/2*sx*sn)
        result.append(f'<path id="provisional-ring-letter-{index:02d}" data-character="{c}" d="{path(gs,gl,transform)}"/>')
    pos+=aa
(HERE/'bc-steamship-token-inscription-provisional.svg').write_text(document(result,1500,1500,'British Columbia Steamship Company — provisional circular inscription','Provisional outlined Euler Fraktur approximation; original engraved letterforms and original font remain unverified. Not an exact token inscription. Baseline radius 550, arc from 212 to 509 degrees clockwise from top, capitals about 100 units.'),encoding='utf-8')
(HERE/'lettering-construction.json').write_text(json.dumps({'wordmark':{'font':SANS,'source_strip_manual_word_extents':words,'regularized_ink_widths':widths,'font_match':'unconfirmed; approximate'},'token_inscription':{'font':FRAKTUR,'status':'provisional; visibly different B/C/S/L and numerals','baseline_radius':R,'start_angle_clockwise_from_top':start,'end_angle_clockwise_from_top':end,'capital_height':100,'horizontal_compression':compression}},indent=2)+'\n')
try:
    import cairosvg
    for name in ['bc-steamship-wordmark-outlined','bc-steamship-token-inscription-provisional']:
        cairosvg.svg2png(url=str(HERE/(name+'.svg')),write_to=str(HERE/(name+'.png')),output_width=1680 if 'wordmark' in name else 1200)
except ImportError:
    pass
print(json.dumps({'files':[str(HERE/'bc-steamship-wordmark-outlined.svg'),str(HERE/'bc-steamship-token-inscription-provisional.svg')],'token_x_compression':compression}))
