"""PGE Point Ellice diamond monogram: hand-fitted monoline reconstruction.

Coordinates are in pixels of the registered 300-dpi crop
(public/identity-collected/pacific-great-eastern-railway/pge-point-ellice-diamond-1929.png).
Diamond centreline and stroke from least-squares line fits to both edges of the printed
diamond; ring from circle fits to its two edges; the P-G-E-R monogram drawn as
monoline strokes (lines and arcs) placed by hand and checked by overlay.
"""
import sys

INK = '#1A1A1A'
# diamond centreline vertices (mean of fitted outer and inner edge intersections)
D = [(194.2, 25.9), (353.1, 222.6), (194.2, 415.9), (34.7, 220.3)]
DW = 12.7
# ring
RC, RR, RW = (194.4, 221.4), 95.7, 9.4
MW = 10.0  # monogram stroke (distance-transform estimate 9-10 px)

P_STEM_X = 188.6


def monogram():
    p = []
    # P: stem (with a short spur left at the top bar) and a bowl whose foot runs into the R
    p.append('M189.5 294.5V150')
    p.append('M184 156.5H228C250 156.5 264 171 264 193C264 214 250 228 232 228H221')
    # E: left of the stem; its bars meet the stem
    p.append('M189.5 196.5H157.6V247H189.5')
    p.append('M157.6 216H179.5')
    # G: open circular arc round the left, with a spur and bar at the lower right
    p.append('M221 190.9A51 51 0 1 0 206 265.2')
    p.append('M199 248.5H228M224 249L214.5 261')
    # R: small bowl right of the stem, diagonal leg
    p.append('M189.5 197H204A15.5 15.5 0 0 1 204 228H189.5')
    p.append('M203.5 229L226 288')
    return ''.join(p)


def svg():
    d = 'M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % tuple(v for pt in D for v in pt)
    body = (
        '<path fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="miter" d="%s"/>' % (INK, DW, d)
        + '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%.1f"/>' % (*RC, RR, INK, RW)
        + '<path fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="butt" stroke-linejoin="miter" d="%s"/>' % (INK, MW, monogram()))
    # tight viewBox: diamond outer vertices (miter extends w/2/sin(half-angle))
    x0, y0, x1, y1 = 25.5, 13.6, 362.3, 428.2
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%.1f" height="%.1f">'
            '<title>Pacific Great Eastern Railway: diamond monogram</title>%s</svg>\n'
            % (x0, y0, x1 - x0, y1 - y0, x1 - x0, y1 - y0, body))


if __name__ == '__main__':
    open(sys.argv[1], 'w').write(svg())
