"""Geometric primitives as (outer polygon, [holes]) for raster fitting and as SVG path data."""
import math
from svgout import num
def ellipse_pts(cx, cy, rx, ry, rot=0, n=120, a0=0, a1=2*math.pi):
    c, s = math.cos(rot), math.sin(rot); out = []
    for i in range(n + 1 if a1 - a0 < 2*math.pi - 1e-9 else n):
        t = a0 + (a1 - a0)*i/(n if a1 - a0 < 2*math.pi - 1e-9 else n)
        x, y = rx*math.cos(t), ry*math.sin(t); out.append((cx + x*c - y*s, cy + x*s + y*c))
    return out
def annulus(cx, cy, rx, ry, t, rot=0):
    return (ellipse_pts(cx, cy, rx, ry, rot), [ellipse_pts(cx, cy, rx - t, ry - t, rot)])
def capsule(x1, y1, x2, y2, w, n=24):
    r = w/2; ang = math.atan2(y2 - y1, x2 - x1)
    pts = []
    for i in range(n + 1):
        a = ang + math.pi/2 + math.pi*i/n; pts.append((x1 + r*math.cos(a), y1 + r*math.sin(a)))
    for i in range(n + 1):
        a = ang - math.pi/2 + math.pi*i/n; pts.append((x2 + r*math.cos(a), y2 + r*math.sin(a)))
    return (pts, [])
def bar(x1, y1, x2, y2, w):
    ang = math.atan2(y2 - y1, x2 - x1); dx, dy = -math.sin(ang)*w/2, math.cos(ang)*w/2
    return ([(x1 + dx, y1 + dy), (x2 + dx, y2 + dy), (x2 - dx, y2 - dy), (x1 - dx, y1 - dy)], [])
# SVG path data (true curves)
def d_ellipse(cx, cy, rx, ry, rot=0, sweep=1):
    deg = math.degrees(rot); c, s = math.cos(rot), math.sin(rot)
    p0 = (cx + rx*c, cy + rx*s); p1 = (cx - rx*c, cy - rx*s)
    return (f"M{num(p0[0])} {num(p0[1])}A{num(rx)} {num(ry)} {num(deg)} 1 {sweep} {num(p1[0])} {num(p1[1])}"
            f"A{num(rx)} {num(ry)} {num(deg)} 1 {sweep} {num(p0[0])} {num(p0[1])}Z")
def d_annulus(cx, cy, rx, ry, t, rot=0):
    return d_ellipse(cx, cy, rx, ry, rot, 1) + d_ellipse(cx, cy, rx - t, ry - t, rot, 0)
def d_capsule(x1, y1, x2, y2, w):
    r = w/2; ang = math.atan2(y2 - y1, x2 - x1); dx, dy = -math.sin(ang)*r, math.cos(ang)*r
    return (f"M{num(x1 + dx)} {num(y1 + dy)}L{num(x2 + dx)} {num(y2 + dy)}A{num(r)} {num(r)} 0 0 0 {num(x2 - dx)} {num(y2 - dy)}"
            f"L{num(x1 - dx)} {num(y1 - dy)}A{num(r)} {num(r)} 0 0 0 {num(x1 + dx)} {num(y1 + dy)}Z")
def d_poly(pts): return 'M' + 'L'.join(f"{num(x)} {num(y)}" for x, y in pts) + 'Z'
