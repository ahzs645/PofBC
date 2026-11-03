#!/usr/bin/env python3
"""Rebuild the early British Columbia Place identity from explicit design geometry.

This is a modern reconstruction, not an extracted historical vector. No image,
font, contour tracing, or optimization library is used to create the SVG paths.
Coordinates are hand specified against the 1983 opening-programme specimen.
See research/identity/bc-place-reconstruction-2026-11-03/README.md.
"""
from math import cos, radians, sin, sqrt
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/identity-collected/bc-place-ltd'
BLUE = '#0096d6'  # Median of a documented patch after applying the PDF's ICC profile.


def n(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.')


def point(cx, cy, r, angle):
    return (cx + r * cos(radians(angle)), cy + r * sin(radians(angle)))


def xy(p):
    return ' '.join(n(v) for v in p)


def circle(cx, cy, r):
    return f'M{n(cx-r)} {n(cy)}a{n(r)} {n(r)} 0 1 0 {n(2*r)} 0a{n(r)} {n(r)} 0 1 0 {n(-2*r)} 0Z'


def ring(cx, cy, r, inner):
    return circle(cx, cy, r) + circle(cx, cy, inner)


def monogram(colour):
    # Three equal outer bowls on an approximately equilateral triangular grid.
    # The narrow echo line is a separate, deliberately open vector stroke.
    bx, by, cx, px, py = 94.5, 161.5, 174.5, 134.5, 231.0
    radius, counter, stem_left, stem_right = 51.0, 28.0, 44.0, 67.0
    pleft, pright, bottom, top = 83.0, 106.0, 347.0, 45.0
    join_top = by - sqrt(radius**2 - ((cx-bx)/2)**2)
    stem_join = by - sqrt(radius**2 - (stem_right-bx)**2)
    lower_join = by + sqrt(radius**2 - (pleft-bx)**2)
    p_join = py + sqrt(radius**2 - (pright-px)**2)
    # Exterior intersection of the c and p circles.
    dx, dy = px-cx, py-by
    distance = sqrt(dx*dx + dy*dy)
    half_chord = sqrt(radius**2 - (distance/2)**2)
    intersection = ((cx+px)/2 + dy/distance*half_chord,
                    (by+py)/2 - dx/distance*half_chord)
    angle = 39.0
    upper_tip = point(cx, by, radius, -angle)
    upper_inner = point(cx, by, counter, -angle)
    lower_inner = point(cx, by, counter, angle)
    lower_tip = point(cx, by, radius, angle)
    d = (f'M{n(stem_left)} {n(top)}H{n(stem_right)}V{n(stem_join)}'
         f'A{radius} {radius} 0 0 1 {n((bx+cx)/2)} {n(join_top)}'
         f'A{radius} {radius} 0 0 1 {xy(upper_tip)}L{xy(upper_inner)}'
         f'A{counter} {counter} 0 1 0 {xy(lower_inner)}L{xy(lower_tip)}'
         f'A{radius} {radius} 0 0 1 {xy(intersection)}'
         f'A{radius} {radius} 0 0 1 {n(pright)} {n(p_join)}'
         f'V{n(bottom)}H{n(pleft)}V{n(lower_join)}'
         f'A{radius} {radius} 0 0 1 {n(stem_left)} {n(by)}Z'
         + circle(bx, by, counter) + circle(px, py, counter))
    echo = 60.5
    echo_left = bx-echo
    echo_pleft = 73.0
    echo_y = by + sqrt(echo**2-(echo_pleft-bx)**2)
    echo_top = by-sqrt(echo**2-((cx-bx)/2)**2)
    echo_b_start = by-sqrt(echo**2-(stem_right-bx)**2)
    echo_pend = py+sqrt(echo**2-(pright-px)**2)
    edx, edy = px-cx, py-by
    ehalf = sqrt(echo**2-(distance/2)**2)
    eintersection = ((cx+px)/2 + edy/distance*ehalf,
                     (by+py)/2-edx/distance*ehalf)
    # Original line is interrupted at the two stem junctions and the c opening.
    line = (f'M{n(echo_left)} {n(top)}V{n(by)}'
            f'A{echo} {echo} 0 0 0 {n(echo_pleft)} {n(echo_y)}V{n(bottom)}'
            f'M{n(stem_right)} {n(echo_b_start)}'
            f'A{echo} {echo} 0 0 1 {n((bx+cx)/2)} {n(echo_top)}'
            f'A{echo} {echo} 0 0 1 {xy(point(cx,by,echo,-angle))}'
            f'M{xy(point(cx,by,echo,angle))}'
            f'A{echo} {echo} 0 0 1 {xy(eintersection)}'
            f'A{echo} {echo} 0 0 1 {n(pright)} {n(echo_pend)}')
    return (f'<g id="bcp-monogram" fill="{colour}">'
            f'<path id="joined-bcp-bowls" fill-rule="evenodd" d="{d}"/>'
            f'<path id="parallel-outline" fill="none" stroke="{colour}" '
            f'stroke-width="3.6" stroke-linecap="butt" stroke-linejoin="round" d="{line}"/>'
            '</g>')


def b_path():
    # Explicit open upper bowl join; the microfiche scan obscures this gap.
    r, q, c, y, cut = 23.5, 10.5, 23.5, 40.5, 16.0
    inner_y = y-sqrt(q*q-(cut-c)**2)
    outer_y = y-sqrt(r*r-(cut-c)**2)
    return (f'M0 0H13V{y}A{q} {q} 0 1 0 {cut} {n(inner_y)}'
            f'V{n(outer_y)}A{r} {r} 0 1 1 0 {y}Z')


def c_path():
    cx, cy, r, q, angle = 23.5, 23.5, 23.5, 11.0, 63.0
    return (f'M{xy(point(cx,cy,r,-angle))}'
            f'A{r} {r} 0 1 0 {xy(point(cx,cy,r,angle))}'
            f'L{xy(point(cx,cy,q,angle))}'
            f'A{q} {q} 0 1 1 {xy(point(cx,cy,q,-angle))}Z')


def a_path():
    r, q, c, y, cut = 23.5, 10.5, 23.5, 23.5, 31.0
    inner_y = y+sqrt(q*q-(cut-c)**2)
    outer_y = y+sqrt(r*r-(cut-c)**2)
    return (f'M47 47H34V{y}A{q} {q} 0 1 0 {cut} {n(inner_y)}'
            f'V{n(outer_y)}A{r} {r} 0 1 1 47 {y}Z')


def e_path():
    c, r, q = 24., 24., 12.
    upper = point(c,c,r,-30)
    total = sum(upper)-2*c
    u = (total-sqrt(2*q*q-total*total))/2
    join = (c+u,c+total-u)
    lower = point(c,c,r,35)
    inner_lower = point(c,c,q,35)
    # The diagonal crossbar has constant width between two parallel lines.
    inner_sum = -6.0
    u0 = (inner_sum-sqrt(2*q*q-inner_sum*inner_sum))/2
    h0, h1 = (c+u0,c+inner_sum-u0), (c+inner_sum-u0,c+u0)
    return (f'M{xy(upper)}L{xy(join)}A{q} {q} 0 0 0 {xy(inner_lower)}'
            f'L{xy(lower)}A{r} {r} 0 1 1 {xy(upper)}Z'
            f'M{xy(h0)}A{q} {q} 0 0 1 {xy(h1)}Z')


def lettering():
    items = []
    def path(label, x, y, d, extra=''):
        items.append(f'<path id="{label}" fill-rule="evenodd" transform="translate({x} {y}){extra}" d="{d}"/>')
    def rect(label,x,y,w,h):
        path(label,x,y,f'M0 0H{w}V{h}H0Z')
    def dot(label,x,y):
        path(label,x,y,circle(0,0,7.15))
    # british: x heights and ascender positions are shared, with optical corrections.
    path('british-b',262,95,b_path())
    path('british-r',313,113,'M0 0H13V3Q17 -1 24 -1V12Q13 12 13 24V46H0Z')
    rect('british-i-1',341,113,13,46); dot('british-i-dot-1',347.5,101.5)
    path('british-t',362,99,'M0 0H13V14H21V26H13V39A8 8 0 0 0 21 47V60H20A20 20 0 0 1 0 40Z')
    rect('british-i-2',389,113,13,46); dot('british-i-dot-2',395.5,101.5)
    path('british-s',407,113,'M37 0H16.5C6 0 0 6.5 0 15.5C0 25 6 30 16.5 30H23C25.5 30 27 31.5 27 34C27 36.5 25.5 37 23 37H0V46H23C33.5 46 39 40 39 30.5C39 21 32.5 16 22 16H16.5C14 16 12.5 14.8 12.5 12.5C12.5 10.2 14 10 16.5 10H37Z')
    path('british-h',450,95,'M0 0H13V20Q17 17 21 17C33 17 41 26 41 38V64H28V38C28 32 25 30 21 30C16 30 13 33 13 38V64H0Z')
    # columbia: the l shares the h's left edge, forming the long vertical stroke.
    path('columbia-c',364,173,c_path())
    path('columbia-o',398,173,ring(24,24,24,11.5))
    rect('shared-h-l-stem',450,157,13,64)
    path('columbia-u',469,174,'M0 0H13V27A7 7 0 0 0 27 27V0H40V27A20 20 0 0 1 0 27Z')
    path('columbia-m',513,174,'M0 47V19A19 19 0 0 1 32 5.1436A19 19 0 0 1 64 19V47H52V20A7 7 0 0 0 38 20V47H26V20A7 7 0 0 0 12 20V47Z')
    path('columbia-b',581,157,b_path())
    rect('columbia-i',633,175,13,46); dot('columbia-i-dot',639.5,164.5)
    path('columbia-a',650,174,a_path())
    # place: p mirrors the b construction, retaining its lower open join.
    path('place-p',289,234,b_path(),' translate(0 64) scale(1 -1)')
    rect('place-l',340,217,13,64)
    path('place-a',358,234,a_path())
    path('place-c',408,234,c_path())
    path('place-e',443,234,e_path())
    return '<g id="custom-wordmark" fill="#000000">'+''.join(items)+'</g>'


def svg(symbol_only=False, colour='#000000'):
    view = '20 32 216 328' if symbol_only else '20 32 690 328'
    width = 216 if symbol_only else 690
    title = 'British Columbia Place — early-1980s '+('monogram' if symbol_only else 'corporate signature')+' — geometric reconstruction'
    description = ('Modern researched reconstruction, made 2026-11-03. Documented historical uses: '
                   'Gulf Islands Driftwood, 22 September 1982, p. 6; BC Place Grand Opening Gala '
                   'programme, 19 June 1983, p. 4 (Canadian Museum of History). '
                   'Hand-built circles, arcs and custom outlined lettering; no raster tracing, '
                   'embedded image, live font or recovered original vector master. '
                   'Designer, exact introduction date and production colour specification unknown.')
    if colour != '#000000':
        description += ' Blue is a representative colour-managed scan sample (#0096d6), not an authenticated brand colour.'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" width="{width}" height="328" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(description)}</desc>\n'
            +monogram(colour)+(lettering() if not symbol_only else '')+'\n</svg>\n')


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    for name, symbol, colour in [
        ('bc-place-1982-monogram-reconstruction.svg',True,'#000000'),
        ('bc-place-1982-lockup-reconstruction.svg',False,'#000000'),
        ('bc-place-1982-lockup-colour-reconstruction.svg',False,BLUE),
    ]:
        target=OUT/name
        target.write_text(svg(symbol,colour),encoding='utf-8')
        print(target.relative_to(ROOT))
