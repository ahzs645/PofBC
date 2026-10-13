#!/usr/bin/env python3
"""Rebuild the supplied BC Forest Service LOOKOUT sign from vector geometry.

No image tracing, font files, embedded bitmap, or image-processing dependency.
Every visible letter is a deliberately constructed polygon / Bezier path.
Python 3.9+; standard library only. Run: python build_sign.py --output ../svg
Optional editable palette/geometry settings: --config design.json
"""
from __future__ import annotations
import argparse, copy, json, math
from pathlib import Path
from xml.sax.saxutils import escape

SVG_NS = 'http://www.w3.org/2000/svg'
INK_NS = 'http://www.inkscape.org/namespaces/inkscape'

DEFAULT = {
    'green': '#00543E', 'red': '#C5001E', 'panel': '#FFFFFF',
    'reference_green': '#03513B', 'reference_red': '#B70416',
    'reference_panel': '#E7ECEB',
    'frame_vertices': [[707,147],[1342,861],[47,861]],
    'panel_offset': 24, 'frame_half_width': 8,
    'inner_vertices': [[706,316],[1105,753],[298,753]],
    'inner_border_width': 13,
    'tight_viewbox': [21,121,1347,766],
    'preview_viewbox': [0,0,1408,1056],
}

def f(x: float) -> str:
    return f'{x:.4f}'.rstrip('0').rstrip('.')

def xy(p): return f'{f(p[0])},{f(p[1])}'

def polygon_path(points):
    return 'M'+xy(points[0])+' '+' '.join('L'+xy(p) for p in points[1:])+' Z'

def outward_normals(points):
    out=[]
    for p,q in zip(points,points[1:]+points[:1]):
        dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
        if length == 0: raise ValueError('Coincident polygon vertices.')
        out.append((dy/length,-dx/length))
    return out

def rounded_offset_path(points, radius):
    """Analytic round-joined offset: three straight edges + three circle arcs."""
    normals=outward_normals(points); starts=[];ends=[]
    for i,p in enumerate(points):
        n0,n1=normals[i-1],normals[i]
        starts.append((p[0]+radius*n0[0],p[1]+radius*n0[1]))
        ends.append((p[0]+radius*n1[0],p[1]+radius*n1[1]))
    out=['M'+xy(starts[0])]
    for i in range(len(points)):
        if i: out.append('L'+xy(starts[i]))
        out.append(f'A{f(radius)},{f(radius)} 0 0 1 '+xy(ends[i]))
    out.append('Z')
    return ' '.join(out)

def inset_polygon(points, distance):
    normals=outward_normals(points);result=[]
    for i,p in enumerate(points):
        n0,n1=normals[i-1],normals[i]
        c0=n0[0]*p[0]+n0[1]*p[1]-distance
        c1=n1[0]*p[0]+n1[1]*p[1]-distance
        det=n0[0]*n1[1]-n0[1]*n1[0]
        if abs(det)<1e-10: raise ValueError('Degenerate polygon corner.')
        result.append(((c0*n1[1]-n0[1]*c1)/det,
                       (n0[0]*c1-c0*n1[0])/det))
    return result

# Bespoke geometric lettering, in local glyph coordinates.
# Tuple: intrinsic width, height, manually authored outline.
GLYPHS = {
 'F': (45,72,'M0 0H45V17H18.2V30H42V46H18.2V72H0Z'),
 'E': (44,72,'M0 0H44V15.5H18.2V27H41.7V43H18.2V56.5H44V72H0Z'),
 'I': (18,72,'M0 0H18V72H0Z'),
 'T': (53,72,'M0 0H53V17H35.9V72H17.1V17H0Z'),
 'H': (53,72,'M0 0H18V29H35V0H53V72H35V46H18V72H0Z'),
 'L': (38,72,'M0 0H18.4V55H38V72H0Z'),
 'V': (62,72,'M0 0H20.6L31 45L41.6 0H62L41.6 72H20.4Z'),
 'M': (64,72,'M0 0H18L32 29L46 0H64V72H46V40L32 72L18 40V72H0Z'),
 'A': (62,72,'M18.8 0H43L62 72H43.2L39.4 59H22.1L18.4 72H0Z '
                  'M26 43.5H35.7L30.9 21.1Z'),
 'O': (67,74,'M33.5 0C13 0 0 13.7 0 37C0 60.8 13 74 33.5 74'
                  'C54 74 67 60.4 67 37C67 13.8 54 0 33.5 0Z '
                  'M33.5 17C24.4 17 20.2 25.5 20.2 37'
                  'C20.2 49 24.4 57 33.5 57C42.6 57 46.8 49 46.8 37'
                  'C46.8 25.5 42.6 17 33.5 17Z'),
 'R': (55,72,'M0 0H26.3C43.9 0 55 10.3 55 26.7'
                  'C55 37.6 49.3 45.2 41.9 49L54.8 72H33L22.5 51.5H18.7V72H0Z '
                  'M18.7 16.4H24.8C32.3 16.4 36.1 20.3 36.1 26.4'
                  'C36.1 32.7 32.4 36.6 24.8 36.6H18.7Z'),
 'B': (55,72,'M0 0H27.5C43.7 0 52 8.2 52 21.3'
                  'C52 27.8 49.1 32.6 44 35.5C51.2 38 55 43.6 55 51.4'
                  'C55 64.3 45.6 72 30.4 72H0Z '
                  'M18 16H25.8C31.8 16 34.2 18.8 34.2 23.3'
                  'C34.2 27.7 31.3 30.4 25.4 30.4H18Z '
                  'M18 43.2H26.6C33.2 43.2 36 45.9 36 50.8'
                  'C36 55.7 33.2 58.4 26.6 58.4H18Z'),
 'U': (49,74,'M0 0H17.8V47.5C17.8 53.6 19.6 56.5 24.5 56.5'
                  'C29.4 56.5 31.2 53.6 31.2 47.5V0H49V47.5'
                  'C49 64.9 39.5 74 24.5 74C9.5 74 0 64.9 0 47.5Z'),
 'C': (64,74,'M64 10L52.6 25.3C47.6 20 43.4 17.4 36 17.4'
                  'C25 17.4 20.5 26.7 20.5 37C20.5 48 25.8 56.9 36.2 56.9'
                  'C43.1 56.9 48.1 54.3 53.3 48.6L64 63.4'
                  'C56.6 70.3 47.6 74 35.5 74C14.4 74 0 58.7 0 37.4'
                  'C0 15.5 14.9 0 36 0C47.8 0 56.6 3.5 64 10Z'),
 'S': (57,74,'M56 9L48.5 25C42.2 20.7 35 17.7 27.7 17.7'
                  'C21.4 17.7 18.7 20.1 18.7 23.5'
                  'C18.7 27.3 23.4 28.5 30.8 30'
                  'C47.7 33.4 57 38.3 57 51.7'
                  'C57 66 45.7 74 28.4 74C17.5 74 6.7 71.1 0 66'
                  'L7.6 50C14.6 54.9 22 57.4 29.4 57.4'
                  'C35.7 57.4 38.4 55.3 38.4 51.8'
                  'C38.4 48 34.8 46.8 26.4 45.2'
                  'C9.5 41.9 .8 36.7 .8 23.2C.8 9.7 11.8 0 28.3 0'
                  'C38.8 0 48.7 3.3 56 9Z'),
}

def layer(label,identifier,contents,color=None,extra=''):
    attrs=f'id="{identifier}" inkscape:groupmode="layer" inkscape:label="{escape(label)}"'
    if color: attrs+=f' fill="{color}"'
    if extra: attrs+=' '+extra
    return f'<g {attrs}>\n{contents}\n</g>'

def path(identifier,d,fill=None,extra=''):
    attrs=f'id="{identifier}" d="{d}" fill-rule="evenodd"'
    if fill: attrs+=f' fill="{fill}"'
    if extra: attrs+=' '+extra
    return f'<path {attrs}/>'

def glyph(letter, x, y, width, height, identifier):
    w,h,d=GLYPHS[letter]
    return path(identifier,d,extra=f'transform="translate({f(x)} {f(y)}) scale({f(width/w)} {f(height/h)})" aria-label="{letter}"')

def green_lettering():
    # Measured character advances, rebuilt on common straight baselines.
    # No pixel contours enter these outlines.
    british=[('B',-1.2,53.8),('R',64.7,51.8),('I',129.8,18.5),
             ('T',159.6,53.2),('I',223.1,18.1),('S',257,55.4),('H',326.4,52.5)]
    b='\n'.join(glyph(c,x,-74.8,w,74.8,f'british-{i+1}-{c}') for i,(c,x,w) in enumerate(british))
    b=f'<g id="word-british" aria-label="BRITISH" transform="translate(366 654) rotate(-46.85)">\n{b}\n</g>'
    columbia=[('C',3.2,58.5,74),('O',63.2,58.6,73.5),('L',129.9,37.9,73.5),
              ('U',170.8,49.2,74),('M',232.6,64.5,73.3),('B',310.4,51.8,73.3),
              ('I',372,18.5,73.3),('A',399.3,61.7,73.3)]
    c='\n'.join(glyph(ch,x,-73.3,w,h,f'columbia-{i+1}-{ch}') for i,(ch,x,w,h) in enumerate(columbia))
    c=f'<g id="word-columbia" aria-label="COLUMBIA" transform="translate(772 363) rotate(47.7)">\n{c}\n</g>'
    bottom=[('F',294,45,72),('O',346,67,74),('R',425,55,72),('E',490,44.5,72),
            ('S',542,57,74),('T',601,53,72),('S',714.5,57,74),('E',782,44.5,72),
            ('R',839,55,72),('V',894,62,72),('I',965,18.5,72),('C',995,64,74),('E',1068,46,72)]
    # Round letters overshoot the common 768–840 cap box by one unit.
    z='\n'.join(glyph(ch,x,767 if h==74 else 768,w,h,f'forest-service-{i+1}-{ch}') for i,(ch,x,w,h) in enumerate(bottom))
    z=f'<g id="word-forest-service" aria-label="FOREST SERVICE">\n{z}\n</g>'
    return b+'\n'+c+'\n'+z

def tall_o(x,y,w,h,hole_width=16):
    """A deliberately drawn narrow O, with nearly parallel counter sides."""
    cx=x+w/2; top=y; bottom=y+h; cy=y+h/2
    # Horizontal tangent controls make rounded heads/feet, not an auto-traced edge.
    side=w*.365
    d=f'M{f(cx)} {f(top)} C{f(cx+side)} {f(top)} {f(x+w)} {f(top+h*.15)} {f(x+w)} {f(cy)} '
    d+=f'C{f(x+w)} {f(bottom-h*.15)} {f(cx+side)} {f(bottom)} {f(cx)} {f(bottom)} '
    d+=f'C{f(cx-side)} {f(bottom)} {f(x)} {f(bottom-h*.15)} {f(x)} {f(cy)} '
    d+=f'C{f(x)} {f(top+h*.15)} {f(cx-side)} {f(top)} {f(cx)} {f(top)} Z '
    hi,lo=y+35,y+h-35; r=hole_width/2
    d+=f'M{f(cx)} {f(hi)} C{f(cx+r*.9)} {f(hi)} {f(cx+r)} {f(hi+(lo-hi)*.17)} {f(cx+r)} {f(cy)} '
    d+=f'C{f(cx+r)} {f(lo-(lo-hi)*.17)} {f(cx+r*.9)} {f(lo)} {f(cx)} {f(lo)} '
    d+=f'C{f(cx-r*.9)} {f(lo)} {f(cx-r)} {f(lo-(lo-hi)*.17)} {f(cx-r)} {f(cy)} '
    d+=f'C{f(cx-r)} {f(hi+(lo-hi)*.17)} {f(cx-r*.9)} {f(hi)} {f(cx)} {f(hi)} Z'
    return d

def lookout_lettering():
    parts=[
      ('lookout-1-L','M447 637L480 604V678H507.5V711.5H447Z'),
      ('lookout-2-O',tall_o(508,542,81,172,14)),
      ('lookout-3-O',tall_o(591,451,95,263,18)),
      ('lookout-4-K','M690 383L707.5 365L727 384V475L750 410L779 440L742 530L775 713H738L725 590V713H690Z'),
      ('lookout-5-O',tall_o(763,490,94,225,18)),
      ('lookout-6-U','M864 536L895 569V675C895 681 896.5 683 900 683'
          'C903.5 683 905 681 905 675V580L933 611V678'
          'C933 702 921 715 900 715C876.5 715 864 702 864 678Z'),
      ('lookout-7-T','M937 616L990 673V700L976 687V714H947V654L937 645Z'),
    ]
    return '\n'.join(path(n,d,extra=f'aria-label="{n[-1]}"') for n,d in parts)

def svg_document(cfg, *, black_background=False, reference_palette=False, separation=None, guides=False):
    view=cfg['preview_viewbox'] if black_background or guides else cfg['tight_viewbox']
    green=cfg['reference_green'] if reference_palette else cfg['green']
    red=cfg['reference_red'] if reference_palette else cfg['red']
    panel=cfg['reference_panel'] if reference_palette else cfg['panel']
    title='British Columbia Forest Service — LOOKOUT — constructed vector sign'
    desc=('Reconstructed from the user-supplied reference. Analytic triangular geometry, '
          'custom Bezier lettering, no traced bitmap, no external font dependencies. '
          'Reconstruction, not an authenticated official artwork master. Colors are approximations.')
    s=[f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="{SVG_NS}" xmlns:inkscape="{INK_NS}" '
       f'width="{f(view[2])}" height="{f(view[3])}" viewBox="'+ ' '.join(f(v) for v in view)+'" role="img" aria-labelledby="sign-title sign-description">',
       '<title id="sign-title">'+escape(title)+'</title>',
       '<desc id="sign-description">'+escape(desc)+'</desc>']
    if black_background:
        s.append(layer('00 · Optional black presentation background','presentation-background',
          '<path d="M0 0H1408V1056H0Z"/>','#000000'))
    if separation is None or separation=='panel':
        s.append(layer('01 · White panel / outer silhouette','panel',
         path('panel-silhouette',rounded_offset_path(cfg['frame_vertices'],cfg['panel_offset'])),panel if not separation else '#000000'))
    if separation is None or separation=='green':
        outer=rounded_offset_path(cfg['frame_vertices'],cfg['frame_half_width'])
        inner=polygon_path(inset_polygon(cfg['frame_vertices'],cfg['frame_half_width']))
        s.append(layer('02 · Outer green border','outer-border',path('outer-border-ring',outer+' '+inner),green))
        d=polygon_path(cfg['inner_vertices'])+' '+polygon_path(inset_polygon(cfg['inner_vertices'],cfg['inner_border_width']))
        s.append(layer('03 · Inner green triangle','inner-border',path('inner-border-ring',d),green))
        s.append(layer('04 · Custom green lettering','green-lettering',green_lettering(),green))
    if separation is None or separation=='red':
        s.append(layer('05 · Custom LOOKOUT lettering','lookout',lookout_lettering(),red,extra='aria-label="LOOKOUT"'))
    if guides:
        items=[f'<path d="{polygon_path(cfg["frame_vertices"])}"/>',
               '<path d="M707 80V950M10 861H1380M250 753H1150M280 768H1130M280 840H1130"/>',
               '<path d="M447 713H990M690 365H727"/>']
        s.append(layer('06 · Construction guides (not production artwork)','construction-guides',
                       '\n'.join(items),'none',extra='stroke="#2979FF" stroke-width="1" stroke-dasharray="7 5"'))
    s.append('</svg>')
    return '\n'.join(s)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent/'svg')
    parser.add_argument('--config',type=Path)
    args=parser.parse_args()
    cfg=copy.deepcopy(DEFAULT)
    if args.config:
        cfg.update(json.loads(args.config.read_text(encoding='utf-8')))
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    variants={
      'BC_Lookout_Master.svg':{},
      'BC_Lookout_Black_Background.svg':{'black_background':True},
      'BC_Lookout_Reference_Palette.svg':{'reference_palette':True},
      'BC_Lookout_Green_Separation.svg':{'separation':'green'},
      'BC_Lookout_Red_Separation.svg':{'separation':'red'},
      'BC_Lookout_Panel_Silhouette.svg':{'separation':'panel'},
      'BC_Lookout_Construction_Guides.svg':{'guides':True},
    }
    for name,kw in variants.items():
        (out/name).write_text(svg_document(cfg,**kw),encoding='utf-8')
    print(f'Created {len(variants)} genuine vector SVG files in {out}')

if __name__=='__main__':
    main()
