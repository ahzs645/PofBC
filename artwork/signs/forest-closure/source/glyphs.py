"""Clean, source-informed geometric lettering. No pixel contours are traced.

Coordinates are typographic construction units, approximately 1000 cap height,
with SVG's downward y direction. Curves are intentional shared masters, not
contour-following splines. Every repeated letter uses the same master.
"""
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from pathlib import Path
import json

K = .5522847498307936

def ellipse(cx,cy,rx,ry,reverse=False):
    if not reverse:
        return (f'M {cx+rx} {cy} C {cx+rx} {cy+K*ry} {cx+K*rx} {cy+ry} {cx} {cy+ry} '
                f'C {cx-K*rx} {cy+ry} {cx-rx} {cy+K*ry} {cx-rx} {cy} '
                f'C {cx-rx} {cy-K*ry} {cx-K*rx} {cy-ry} {cx} {cy-ry} '
                f'C {cx+K*rx} {cy-ry} {cx+rx} {cy-K*ry} {cx+rx} {cy} Z')
    return (f'M {cx+rx} {cy} C {cx+rx} {cy-K*ry} {cx+K*rx} {cy-ry} {cx} {cy-ry} '
            f'C {cx-K*rx} {cy-ry} {cx-rx} {cy-K*ry} {cx-rx} {cy} '
            f'C {cx-rx} {cy+K*ry} {cx-K*rx} {cy+ry} {cx} {cy+ry} '
            f'C {cx+K*rx} {cy+ry} {cx+rx} {cy+K*ry} {cx+rx} {cy} Z')

GLYPHS = {
 'A': 'M 330 0 H 600 L 950 1000 H 665 L 590 790 H 325 L 250 1000 H 0 Z M 355 565 H 555 L 460 300 Z',
 'B': 'M 0 0 H 355 C 610 0 720 90 720 263 C 720 365 665 438 588 474 C 705 510 778 598 778 729 C 778 912 635 1000 390 1000 H 0 Z M 265 225 V 390 H 365 C 438 390 478 360 478 309 C 478 255 438 225 365 225 Z M 265 600 V 790 H 380 C 480 790 523 754 523 695 C 523 633 474 600 380 600 Z',
 'C': 'M 850 115 L 730 350 C 660 290 585 250 480 250 C 330 250 250 350 250 500 C 250 650 330 750 480 750 C 585 750 660 710 730 650 L 850 885 C 740 970 610 1010 460 1010 C 180 1010 0 810 0 500 C 0 190 180 -10 460 -10 C 610 -10 740 30 850 115 Z',
 'D': 'M 0 0 H 320 C 670 0 840 170 840 500 C 840 830 670 1000 320 1000 H 0 Z M 265 245 V 755 H 320 C 485 755 565 665 565 500 C 565 335 485 245 320 245 Z',
 'E': 'M 0 0 H 680 V 250 H 260 V 360 H 640 V 600 H 260 V 740 H 680 V 1000 H 0 Z',
 'F': 'M 0 0 H 670 V 230 H 260 V 370 H 620 V 610 H 260 V 1000 H 0 Z',
 'L': 'M 0 0 H 270 V 755 H 665 V 1000 H 0 Z',
 'N': 'M 0 0 H 250 L 520 430 V 0 H 770 V 1000 H 520 L 250 400 V 1000 H 0 Z',
 'O': ellipse(475,500,475,510)+ellipse(475,500,215,260,True),
 'P': 'M 0 0 H 380 C 660 0 800 120 800 350 C 800 570 660 700 380 700 H 270 V 1000 H 0 Z M 270 235 V 465 H 375 C 475 465 530 430 530 350 C 530 270 475 235 375 235 Z',
 'R': 'M 0 0 H 380 C 660 0 800 120 800 350 C 800 520 725 625 585 685 L 785 1000 H 510 L 330 710 H 265 V 1000 H 0 Z M 250 225 V 465 H 390 C 495 465 550 430 550 350 C 550 270 495 225 390 225 Z',
 'S': 'M 855 85 L 755 320 C 665 270 565 240 450 240 C 350 240 290 260 290 300 C 290 335 350 350 460 380 L 565 410 C 760 470 835 585 835 735 C 835 920 680 1010 435 1010 C 260 1010 100 955 0 885 L 100 650 C 220 730 350 770 465 770 C 555 770 600 745 600 705 C 600 660 545 645 435 610 L 330 580 C 120 520 30 425 30 280 C 30 110 180 -10 420 -10 C 585 -10 740 25 855 85 Z',
 'T': 'M 0 0 H 900 V 260 H 560 V 1000 H 285 V 260 H 0 Z',
 'U': 'M 0 0 H 265 V 650 C 265 755 295 790 400 790 C 505 790 535 755 535 650 V 0 H 800 V 675 C 800 900 680 1010 400 1010 C 120 1010 0 900 0 675 Z',
 'V': 'M 0 0 H 280 L 485 650 L 690 0 H 970 L 620 1000 H 350 Z',
 'W': 'M 0 0 H 265 L 390 610 L 530 0 H 780 L 920 610 L 1045 0 H 1310 L 1065 1000 H 790 L 655 430 L 520 1000 H 245 Z',
 'Y': 'M 0 0 H 285 L 500 305 L 715 0 H 1000 L 625 610 V 1000 H 350 V 610 Z',
 'Z': 'M 0 0 H 800 L 345 790 H 800 V 1000 H 0 L 455 210 H 0 Z',
 '3': 'M 65 65 C 230 -5 500 -30 685 60 C 875 150 860 350 665 455 C 890 510 945 630 860 795 C 735 1020 300 1040 0 920 L 65 725 C 225 855 475 865 590 775 C 695 675 600 550 400 550 H 295 V 360 C 415 370 570 360 600 285 C 635 205 470 170 320 180 C 240 188 155 205 115 235 Z',
}

def bounds(d):
    p=BoundsPen(None);parse_path(d,p);return p.bounds

def normalized(d):
    x0,y0,x1,y1=bounds(d)
    p=SVGPathPen(None)
    parse_path(d,TransformPen(p,(1,0,0,1000/(y1-y0),-x0,-y0*1000/(y1-y0))))
    return p.getCommands(),x1-x0

NORMALIZED={k:normalized(v) for k,v in GLYPHS.items()}

def build_font(destination,normalized_glyphs=None,family='Forest Closure 1960 Reconstruction'):
    normalized_glyphs=normalized_glyphs or NORMALIZED
    chars=sorted(normalized_glyphs)
    psname=family.replace(' ','')+'-Heavy'
    names={c:('three' if c=='3' else c) for c in chars}
    order=['.notdef','space']+[names[c] for c in chars]
    fb=FontBuilder(1400,isTTF=False);fb.setupGlyphOrder(order)
    fb.setupCharacterMap({32:'space',**{ord(c):names[c] for c in chars}})
    cs={};metrics={}
    for c in [None,' ']+chars:
        name='.notdef' if c is None else ('space' if c==' ' else names[c])
        if c in normalized_glyphs:
            d,w=normalized_glyphs[c];advance=round(w+90)
            pen=T2CharStringPen(advance,None)
            parse_path(d,TransformPen(pen,(1,0,0,-1,45,1000)))
        else:
            advance=400;pen=T2CharStringPen(advance,None)
        cs[name]=pen.getCharString();metrics[name]=(advance,45 if c in normalized_glyphs else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1100,descent=-300)
    fb.setupNameTable({'familyName':family,'styleName':'Heavy',
      'uniqueFontIdentifier':psname+'-1.0','fullName':family+' Heavy',
      'psName':psname,'version':'Version 1.000',
      'copyright':'Original geometric reconstruction prepared for Ahmad Jalil, 2026. Historical attribution not claimed.',
      'description':'Source-informed uppercase specimen subset; original geometric masters. Not an authenticated historical typeface.'})
    fb.setupOS2(sTypoAscender=1100,sTypoDescender=-300,sTypoLineGap=0,usWinAscent=1100,usWinDescent=300,sCapHeight=1000,sxHeight=700,usWeightClass=900)
    fb.setupPost();fb.setupCFF(psname,{'FullName':family+' Heavy','FamilyName':family,'Weight':'Heavy'},cs,{})
    fb.setupMaxp();fb.save(str(destination))

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]
    build_font(out/'fonts/ForestClosure1960-Reconstruction.otf')
    (out/'source/glyph_masters.json').write_text(json.dumps({k:{'path':v[0],'width':v[1],'cap_height':1000} for k,v in NORMALIZED.items()},indent=2))
    print('Built',len(GLYPHS),'original shared glyph masters')
