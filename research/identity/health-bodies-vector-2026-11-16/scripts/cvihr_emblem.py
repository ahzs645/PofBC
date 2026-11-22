"""Central Vancouver Island Health Region — mountain-and-wave emblem, VECTOR RECONSTRUCTION.

  python -I cvihr_emblem.py

Fitted by hand to the 232 x 112 grayscale emblem of May 1999 (the repo's
central-vancouver-island-health-region-1999-grayscale-emblem.png, from The World Without Linen
Bags, PDF page 85). The four mountains are drawn as triangles with 45-degree sides, cut off along the wave's top edge (all four apexes
and edges measured on the scan fit that slope); the front mountain is lighter. The wave band, its two
left streamers and its two right points are one path through hand-picked points, smoothed as
Catmull-Rom curves. No bitmap tracing. Greys are averages measured on the scan, approximations only;
the scan is a halftoned photocopy, and the emblem's original colours are not known.
Coordinates are the scan's pixels.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "public/identity-collected/central-vancouver-island-health-region/central-vancouver-island-health-region-1999-emblem-rebuilt.svg"
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")

def mountain(ax, ay, base=96):
    h = base - ay
    return f"M{f(ax)} {f(ay)}L{f(ax + h)} {f(base)}L{f(ax - h)} {f(base)}Z"

def catmull(pts, closed=False):
    """Catmull-Rom through pts, as cubic Beziers (tension 0.5); returns path commands after the first point."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return "".join(out)

# wave band: top edge (in front of the mountains), right points, bottom edge, left streamers
top = [(12.5, 77.5), (45, 72.6), (81.7, 67.4), (100, 73.2), (120, 78.2), (150, 80.2), (172, 79.6), (188, 77.4), (205, 72.5), (220.8, 67.6)]
bottom = [(227.6, 79.6), (216.7, 90), (203.3, 99.6), (186.7, 104.8), (166.7, 106.6), (141.7, 105), (116.7, 100.3), (93.3, 94.3), (76.7, 91.5), (55, 91), (33.3, 92), (16.7, 95.4), (4, 100.6)]
band = ("M" + f"{f(top[0][0])} {f(top[0][1])}" + catmull(top)
        + "L216.6 72.6L218.6 76.4L206.4 86.2L" + f"{f(bottom[0][0])} {f(bottom[0][1])}" + catmull(bottom)
        + "L34.2 82.8L6.6 85L16.8 80.2Z")
DARK, MID, LIGHT, BAND = "#3e3e3e", "#434343", "#5b5b5b", "#383838"
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="3.5 4.5 225 103">'
       '<title>Central Vancouver Island Health Region — emblem (vector reconstruction)</title>'
       '<desc>Hand-fitted reconstruction of the grayscale mountain-and-wave emblem seen in May 1999; greys approximate the scan.</desc>'
       f'<defs><clipPath id="above-wave"><path d="M{f(top[0][0])} {f(top[0][1])}{catmull(top)}L232 67.6L232 0L0 0L0 77.5Z"/></clipPath></defs>'
       '<g clip-path="url(#above-wave)">'
       f'<path d="{mountain(101.2, 5)}" fill="{DARK}"/>'
       f'<path d="{mountain(156.2, 12.6)}" fill="{DARK}"/>'
       f'<path d="{mountain(74.6, 16.2)}" fill="{MID}"/>'
       f'<path d="{mountain(130.5, 20)}" fill="{LIGHT}"/></g>'
       f'<path d="{band}" fill="{BAND}"/>'
       '</svg>\n')
OUT.write_text(svg)
print(OUT)
