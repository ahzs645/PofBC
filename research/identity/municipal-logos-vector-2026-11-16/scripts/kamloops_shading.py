"""Kamloops logo, from the back cover (page 142) of the City's 2025 Annual Report.

The logo is drawn there as vector paths, but its colour ramps are PDF axial shadings (`sh`) painted
inside clipping paths, which PyMuPDF's get_drawings() does not report. This script reads the logo's
own marked-content block (/PlacedGraphic /MC0) from the page's content stream and replays it:
every path, clip and fill is the PDF's own geometry; every axial shading becomes an SVG
linearGradient with the shading's own axis (its matrix), its own stops (from the stitching
function's bounds) and its own colours. CMYK and the Cyan separation are converted to RGB by MuPDF
(the same conversion get_drawings() applies elsewhere in this package). Nothing is traced or
redrawn.

    python3 -I kamloops_shading.py <downloads-dir>

Writes public/identity-municipal/kamloops/annual-report-2025-logo.svg.
"""
import hashlib
import re
import sys
from pathlib import Path

import pymupdf

SOURCE_SHA256 = "bca9635d5c7829f169df031f45b24bad63b3910ea87dda0f8272ec2b90765440"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / "public/identity-municipal/kamloops/annual-report-2025-logo.svg"
PAGE = 142

pdf = Path(sys.argv[1]) / "kamloops/annual-report-2025.pdf"
data = pdf.read_bytes()
if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
    sys.exit("The PDF is not the 2025 Annual Report this extraction was checked against.")
doc = pymupdf.open(stream=data, filetype="pdf")
page = doc[PAGE - 1]
H = page.rect.height
content = page.read_contents().decode("latin1")

# The logo's marked-content block.
start = content.index("/PlacedGraphic /MC0 BDC")
depth = 0
for m in re.finditer(r"\b(BDC|BMC|EMC)\b", content[start:]):
    depth += -1 if m.group() == "EMC" else 1
    if depth == 0:
        block = content[start:start + m.end()]
        break

# Colour conversion by MuPDF: paint each colour on a scratch page and read it back.
_cache = {}


def rgb_of(op, comps):
    key = (op, tuple(round(c, 5) for c in comps))
    if key not in _cache:
        scratch = pymupdf.open()
        sp = scratch.new_page(width=10, height=10)
        stream = f"{' '.join(f'{c:.5f}' for c in comps)} {op} 0 0 10 10 re f".encode()
        xref = scratch.get_new_xref()
        scratch.update_object(xref, "<<>>")
        scratch.update_stream(xref, stream)
        scratch.xref_set_key(sp.xref, "Contents", f"{xref} 0 R")
        fill = sp.get_drawings()[0]["fill"]
        _cache[key] = "#%02x%02x%02x" % tuple(round(v * 255) for v in fill)
    return _cache[key]


def resolve(obj):
    """Return the object's dictionary source for an indirect ref or inline text."""
    m = re.fullmatch(r"\s*(\d+) 0 R\s*", obj)
    return doc.xref_object(int(m.group(1)), compressed=True) if m else obj


def key_of(src, key):
    t, v = doc.xref_get_key(int(src), key) if isinstance(src, int) else (None, None)
    return t, v


def nums(s):
    return [float(x) for x in re.findall(r"-?\d*\.?\d+", s)]


def shading_stops(sh_xref):
    """Stops of an axial shading whose function is a type-3 stitch of type-2 functions."""
    _, cs = doc.xref_get_key(sh_xref, "ColorSpace")
    _, coords = doc.xref_get_key(sh_xref, "Coords")
    assert nums(coords) == [0, 0, 1, 0], coords
    _, fref = doc.xref_get_key(sh_xref, "Function")
    fx = int(fref.split()[0])
    assert doc.xref_get_key(fx, "FunctionType")[1] == "3"
    bounds = nums(doc.xref_get_key(fx, "Bounds")[1])
    encode = nums(doc.xref_get_key(fx, "Encode")[1])
    subs = [int(r) for r in re.findall(r"(\d+) 0 R", doc.xref_get_key(fx, "Functions")[1])]
    edges = [0.0] + bounds + [1.0]
    if cs == "/DeviceCMYK":
        to_rgb = lambda c: rgb_of("k", c)
    else:  # a Separation (Cyan) whose tint transform is linear to CMYK
        csx = int(cs.split()[0])
        arr = doc.xref_object(csx, compressed=True)
        c0 = nums(re.search(r"/C0\s*\[([^\]]*)\]", arr).group(1))
        c1 = nums(re.search(r"/C1\s*\[([^\]]*)\]", arr).group(1))
        to_rgb = lambda t: rgb_of("k", [a + t[0] * (b - a) for a, b in zip(c0, c1)])
    stops = []
    for i, sx in enumerate(subs):
        if doc.xref_get_key(sx, "FunctionType")[1] == "0":
            # A sampled function (64 CMYK samples, linear interpolation): each sample is a stop.
            size = int(nums(doc.xref_get_key(sx, "Size")[1])[0])
            assert doc.xref_get_key(sx, "BitsPerSample")[1] == "8" and nums(doc.xref_get_key(sx, "Encode")[1]) == [0, size - 1]
            ncomp = len(nums(doc.xref_get_key(sx, "Range")[1])) // 2
            raw = doc.xref_stream(sx)
            e0, e1 = encode[2 * i], encode[2 * i + 1]
            a, b = edges[i], edges[i + 1]
            for s in range(size):
                x = s / (size - 1)  # position in the sub-function's domain
                u = (x - e0) / (e1 - e0)
                col = [raw[s * ncomp + k] / 255 for k in range(ncomp)]
                stops.append((a + u * (b - a), to_rgb(col)))
            continue
        assert doc.xref_get_key(sx, "FunctionType")[1] == "2"
        n = float(doc.xref_get_key(sx, "N")[1])
        C0 = nums(doc.xref_get_key(sx, "C0")[1])
        C1 = nums(doc.xref_get_key(sx, "C1")[1])
        e0, e1 = encode[2 * i], encode[2 * i + 1]
        a, b = edges[i], edges[i + 1]
        steps = 1 if n == 1 else 8  # a non-linear segment is sampled, linearly between samples
        for s in range(steps + 1):
            u = s / steps
            x = e0 + u * (e1 - e0)
            col = [p + (x ** n) * (q - p) for p, q in zip(C0, C1)]
            stops.append((a + u * (b - a), to_rgb(col)))
    return stops


res_sh = dict(re.findall(r"/(Sh\d+) (\d+) 0 R", doc.xref_get_key(page.xref, "Resources")[1]))


def mul(m1, m2):
    a, b, c, d, e, f = m1
    A, B, C, D, E, F = m2
    return (a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, e * A + f * C + E, e * B + f * D + F)


FLIP = (1, 0, 0, -1, 0, H)
num = lambda v: f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) >= 0.0005 else "0"


def pt(x, y, m):
    a, b, c, d, e, f = mul(m, FLIP)
    return a * x + c * y + e, b * x + d * y + f


tokens = re.findall(r"/\w+|-?\d*\.\d+|-?\d+|[A-Za-z*'\"]+", block)
stack = []
gs = {"ctm": (1, 0, 0, 1, 0, 0), "fill": "#000000", "clip": None}
gstack = []
path, cur, start_pt = [], None, None
pending_clip = None
defs, body = [], []
clip_n = grad_n = 0
bbox = [1e9, 1e9, -1e9, -1e9]


def track(x, y):
    bbox[0] = min(bbox[0], x); bbox[1] = min(bbox[1], y); bbox[2] = max(bbox[2], x); bbox[3] = max(bbox[3], y)


def d_of(segments):
    return "".join(segments)


for tok in tokens:
    if re.fullmatch(r"-?\d*\.?\d+", tok) or tok.startswith("/"):
        stack.append(tok)
        continue
    a = [float(s) for s in stack if not s.startswith("/")]
    names = [s for s in stack if s.startswith("/")]
    stack = []
    m = gs["ctm"]
    if tok == "q":
        gstack.append(dict(gs))
    elif tok == "Q":
        gs = gstack.pop() if gstack else gs
    elif tok == "cm":
        gs["ctm"] = mul(tuple(a), gs["ctm"])
    elif tok == "m":
        x, y = pt(a[0], a[1], m); path.append(f"M{num(x)} {num(y)}"); cur = (a[0], a[1]); start_pt = cur
    elif tok == "l":
        x, y = pt(a[0], a[1], m); path.append(f"L{num(x)} {num(y)}"); cur = (a[0], a[1])
    elif tok in ("c", "v", "y"):
        if tok == "c":
            p1, p2, p3 = (a[0], a[1]), (a[2], a[3]), (a[4], a[5])
        elif tok == "v":
            p1, p2, p3 = cur, (a[0], a[1]), (a[2], a[3])
        else:
            p1, p2, p3 = (a[0], a[1]), (a[2], a[3]), (a[2], a[3])
        path.append("C" + " ".join(f"{num(u)} {num(w)}" for u, w in (pt(*p1, m), pt(*p2, m), pt(*p3, m))))
        cur = p3
    elif tok == "re":
        x, y, w, h = a
        corners = [pt(x, y, m), pt(x + w, y, m), pt(x + w, y + h, m), pt(x, y + h, m)]
        path.append("M" + "L".join(f"{num(u)} {num(v)}" for u, v in corners) + "Z")
    elif tok == "h":
        path.append("Z")
    elif tok in ("W", "W*"):
        pending_clip = (d_of(path), "evenodd" if tok == "W*" else "nonzero")
    elif tok in ("f", "F", "f*", "n"):
        if tok != "n":
            rule = ' fill-rule="evenodd"' if tok == "f*" else ""
            cp = f' clip-path="url(#{gs["clip"]})"' if gs["clip"] else ""
            body.append(f'<path d="{d_of(path)}" fill="{gs["fill"]}"{rule}{cp}/>')
        if pending_clip:
            clip_n += 1
            cid = f"c{clip_n}"
            parent = f' clip-path="url(#{gs["clip"]})"' if gs["clip"] else ""
            defs.append(f'<clipPath id="{cid}"{parent}><path d="{pending_clip[0]}" clip-rule="{pending_clip[1]}"/></clipPath>')
            gs["clip"] = cid
            if clip_n == 1:  # the placed graphic's own bounding clip
                for seg in re.findall(r"-?\d*\.?\d+ -?\d*\.?\d+", pending_clip[0]):
                    track(*map(float, seg.split()))
            pending_clip = None
        path = []
    elif tok == "k":
        gs["fill"] = rgb_of("k", a)
    elif tok == "g":
        gs["fill"] = rgb_of("g", a)
    elif tok == "sh":
        grad_n += 1
        gid = f"g{grad_n}"
        stops = shading_stops(int(res_sh[names[0][1:]]))
        mm = mul(m, FLIP)
        defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1" y2="0" '
                    f'gradientTransform="matrix({" ".join(num(v) for v in mm)})">'
                    + "".join(f'<stop offset="{num(o)}" stop-color="{c}"/>' for o, c in stops) + "</linearGradient>")
        body.append(f'<rect x="{num(bbox[0])}" y="{num(bbox[1])}" width="{num(bbox[2] - bbox[0])}" height="{num(bbox[3] - bbox[1])}" '
                    f'fill="url(#{gid})" clip-path="url(#{gs["clip"]})"/>')
    elif tok in ("BDC", "BMC", "EMC", "BX", "EX", "gs", "d", "w", "j", "J", "M", "i", "ri"):
        pass
    else:
        raise SystemExit(f"unhandled operator {tok}")

vb = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(num(v) for v in vb)}" width="{num(vb[2] * 4)}" height="{num(vb[3] * 4)}">'
       "<title>City of Kamloops</title><defs>" + "".join(defs) + "</defs>" + "".join(body) + "</svg>\n")
OUT.write_text(svg)
print(f"{OUT.relative_to(ROOT)}: {len(body)} shapes ({grad_n} gradients, {clip_n} clips), {len(svg)} bytes, sha256 {hashlib.sha256(svg.encode()).hexdigest()}")
