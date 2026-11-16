"""Write clean SVGs from lists of (d, fill[, extra]) with a tight viewBox."""
import hashlib, re
def num(v): return f"{v:.2f}".rstrip('0').rstrip('.')
def poly_d(pts): return 'M' + ' L'.join(f"{num(x)} {num(y)}" for x, y in pts) + 'Z'
def write(path, shapes, box, title, margin=0.5, scale=4):
    x0, y0, x1, y1 = box
    vb = (x0 - margin, y0 - margin, x1 - x0 + 2*margin, y1 - y0 + 2*margin)
    body = ''.join(f'<path d="{d}" fill="{f}"{(" " + e) if e else ""}/>' for d, f, *rest in shapes for e in [rest[0] if rest else ''])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(num(v) for v in vb)}" '
           f'width="{num(vb[2]*scale)}" height="{num(vb[3]*scale)}"><title>{title}</title>{body}</svg>\n')
    open(path, 'w').write(svg)
    assert '<image' not in svg and '<text' not in svg
    return hashlib.sha256(svg.encode()).hexdigest(), len(svg.encode())
