"""Shared helpers: pull filled/stroked vector paths out of a PDF page region with PyMuPDF and
write them to a clean SVG (page coordinates, tight viewBox, explicit fills, no images or text).
The paths and their colours are the PDF's own (MuPDF's conversion of the PDF colour to sRGB)."""
import hashlib
import pymupdf as fitz

num = lambda v: f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) >= 0.0005 else "0"
hexof = lambda rgb: "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb[:3])


def path_d(items):
    d, at = [], None
    for item in items:
        kind, *pts = item
        if kind == "re":
            r = pts[0]
            d.append(f"M{num(r.x0)} {num(r.y0)}H{num(r.x1)}V{num(r.y1)}H{num(r.x0)}Z"); at = None; continue
        if kind == "qu":
            q = pts[0]
            d.append("M" + " L".join(f"{num(p.x)} {num(p.y)}" for p in (q.ul, q.ur, q.lr, q.ll)) + "Z"); at = None; continue
        start = pts[0]
        if at is None or abs(at.x - start.x) > 1e-3 or abs(at.y - start.y) > 1e-3:
            if d and not d[-1].endswith("Z"):
                d.append("Z")
            d.append(f"M{num(start.x)} {num(start.y)}")
        if kind == "l":
            d.append(f"L{num(pts[1].x)} {num(pts[1].y)}")
        elif kind == "c":
            d.append("C" + " ".join(f"{num(p.x)} {num(p.y)}" for p in pts[1:]))
        at = pts[-1]
    s = "".join(d)
    return s if s.endswith("Z") else s + "Z"


def drawings_in(page, clip, keep=lambda d: True):
    clip = fitz.Rect(clip)
    return [d for d in page.get_drawings() if clip.contains(d["rect"]) and keep(d)]


def svg_of(drawings, title, desc="", pad=0.0, colour_map=None):
    box = fitz.Rect(drawings[0]["rect"])
    for d in drawings:
        box |= d["rect"]
    parts = []
    for d in drawings:
        dd = path_d(d["items"])
        attrs = []
        if d.get("fill") is not None:
            c = hexof(d["fill"]); c = (colour_map or {}).get(c, c)
            attrs.append(f'fill="{c}"')
            if d.get("even_odd"):
                attrs.append('fill-rule="evenodd"')
            if d.get("fill_opacity", 1) < 1:
                attrs.append(f'fill-opacity="{num(d["fill_opacity"])}"')
        else:
            attrs.append('fill="none"')
        if d.get("color") is not None and d["type"] in ("s", "fs"):
            c = hexof(d["color"]); c = (colour_map or {}).get(c, c)
            attrs.append(f'stroke="{c}" stroke-width="{num(d.get("width") or 1)}"')
            if d.get("lineJoin") is not None: pass
        parts.append(f'<path d="{dd}" {" ".join(attrs)}/>')
    x, y, w, h = box.x0 - pad, box.y0 - pad, box.width + 2 * pad, box.height + 2 * pad
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x)} {num(y)} {num(w)} {num(h)}">'
            f'<title>{esc(title)}</title>' + (f'<desc>{esc(desc)}</desc>' if desc else "") + "".join(parts) + "</svg>\n")


def sha(path):
    b = open(path, "rb").read()
    return hashlib.sha256(b).hexdigest(), len(b)


def svg_with_clips(page, keep_rect, title, desc="", view=None):
    """Like svg_of, but honours PyMuPDF's extended clip stack (get_drawings(extended=True)):
    each 'clip' entry applies to the following entries of deeper level. Fill/stroke entries whose
    rect lies inside keep_rect are written; clips are written only around kept content.
    view: optional fitz.Rect for the viewBox (defaults to the kept paths' union)."""
    keep_rect = fitz.Rect(keep_rect)
    ext = page.get_drawings(extended=True)
    defs, body, stack, union, n = [], [], [], None, 0
    open_groups = []  # (level, state): state = clip id not yet written, True once its <g> is open, None/False otherwise

    def close_to(level):
        while open_groups and open_groups[-1][0] >= level:
            lvl, state = open_groups.pop()
            if state is True:
                body.append("</g>")

    for e in ext:
        lvl = e.get("level", 0)
        if e["type"] in ("clip", "group"):
            close_to(lvl)
            if e["type"] == "clip":
                cid = f"c{len(defs)}"
                rule = ' clip-rule="evenodd"' if e.get("even_odd") else ""
                defs.append(f'<clipPath id="{cid}"><path d="{path_d(e["items"])}"{rule}/></clipPath>')
                open_groups.append((lvl, cid))
            else:
                open_groups.append((lvl, None))
            continue
        close_to(lvl)
        if not keep_rect.contains(e["rect"]):
            continue
        # open any pending clip groups
        for k, (l, cid) in enumerate(open_groups):
            if isinstance(cid, str):
                body.append(f'<g clip-path="url(#{cid})">'); open_groups[k] = (l, True)
            elif cid is None:
                open_groups[k] = (l, False)
        a = []
        if e.get("fill") is not None:
            a.append(f'fill="{hexof(e["fill"])}"' + (' fill-rule="evenodd"' if e.get("even_odd") else ""))
            if (e.get("fill_opacity") or 1) < 1: a.append(f'fill-opacity="{num(e["fill_opacity"])}"')
        else:
            a.append('fill="none"')
        if e["type"] in ("s", "fs") and e.get("color") is not None:
            a.append(f'stroke="{hexof(e["color"])}" stroke-width="{num(e.get("width") or 0.35)}"')
        body.append(f'<path d="{path_d(e["items"])}" {" ".join(a)}/>')
        union = fitz.Rect(e["rect"]) if union is None else union | e["rect"]
        n += 1
    close_to(-1)
    v = view or union
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(v.x0)} {num(v.y0)} {num(v.width)} {num(v.height)}">'
           f'<title>{esc(title)}</title>' + (f'<desc>{esc(desc)}</desc>' if desc else "")
           + "<defs>" + "".join(d for d in defs if f'url(#{d.split(chr(34))[1]})' in "".join(body)) + "</defs>" + "".join(body) + "</svg>\n")
    return svg, n, union
