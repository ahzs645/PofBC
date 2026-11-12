"""Innovate BC logo, from the cover of its 2024/2025 Impact Report.

The cover sets the logo as vector paths: the "innovate BC" wordmark (dark grey with "BC" in teal) and
the white "i". The disc behind the "i" is a 252 x 252 photograph of star trails, clipped to a circle;
it is the logo's texture, so it is kept: converted from the PDF's CMYK to RGB by MuPDF, embedded as a
JPEG, and clipped by the cover's own circle, placed where the cover places it. Every other shape is
the PDF's own path, in the PDF's own colours.

    python -I research/identity/innovate-bc-vector-2026-11-12/extract.py path/to/Impact-Report_2024-2025_FINAL-PORTRAIT-1.pdf

Needs PyMuPDF 1.26.6. Writes public/identity-collected/innovate-bc/innovate-bc-2024-colour.svg.
"""
import hashlib
import sys
from pathlib import Path

import base64
import io

import fitz
from PIL import Image

SOURCE_SHA256 = "8858c0093a0cd93a13f193d1bdd42d0191f61e000a627f0c8309b6b1f86d6ed4"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "public/identity-collected/innovate-bc/innovate-bc-2024-colour.svg"
# The logo's box on page 1, in PDF points: the disc's clip and the wordmark under it.
LOGO = fitz.Rect(30, 660, 170, 760)
DISC_XREF = 1069

pdf = Path(sys.argv[1])
data = pdf.read_bytes()
if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
    sys.exit("The PDF is not the 2024/2025 Impact Report this extraction was checked against.")
page = fitz.open(stream=data, filetype="pdf")[0]

hexof = lambda rgb: "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)
num = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")


def path_of(items):
    d, at = [], None
    for item in items:
        kind, *pts = item
        if kind == "re":
            r = pts[0]
            d.append(f"M{num(r.x0)} {num(r.y0)}H{num(r.x1)}V{num(r.y1)}H{num(r.x0)}Z")
            at = None
            continue
        if kind == "qu":
            q = pts[0]
            d.append("M" + " L".join(f"{num(p.x)} {num(p.y)}" for p in (q.ul, q.ur, q.lr, q.ll)) + "Z")
            at = None
            continue
        start = pts[0]
        if at is None or abs(at.x - start.x) > 1e-3 or abs(at.y - start.y) > 1e-3:
            if d:
                d.append("Z")
            d.append(f"M{num(start.x)} {num(start.y)}")
        if kind == "l":
            d.append(f"L{num(pts[1].x)} {num(pts[1].y)}")
        elif kind == "c":
            d.append("C" + " ".join(f"{num(p.x)} {num(p.y)}" for p in pts[1:]))
        at = pts[-1]
    return "".join(d) + "Z"


# The disc: the clip path the photograph is drawn inside.
disc = next(dr for dr in page.get_drawings(extended=True)
            if dr["type"] == "clip" and dr.get("scissor") and abs(dr["scissor"].x0 - 69.1) < 0.5 and abs(dr["scissor"].y0 - 667.5) < 0.5)
doc = page.parent
photo = fitz.Pixmap(doc, DISC_XREF)
if photo.colorspace.n != 3:
    photo = fitz.Pixmap(fitz.csRGB, photo)
jpeg = io.BytesIO()
Image.frombytes("RGB", (photo.width, photo.height), photo.samples).save(jpeg, "JPEG", quality=92)
placed = next(info["bbox"] for info in page.get_image_info(xrefs=True) if info["xref"] == DISC_XREF)
shapes = [
    f'<clipPath id="disc"><path d="{path_of(disc["items"])}"/></clipPath>'
    f'<image clip-path="url(#disc)" x="{num(placed[0])}" y="{num(placed[1])}" width="{num(placed[2] - placed[0])}" height="{num(placed[3] - placed[1])}" '
    f'preserveAspectRatio="none" href="data:image/jpeg;base64,{base64.b64encode(jpeg.getvalue()).decode()}"/>'
]
for dr in page.get_drawings():
    if dr["type"] != "f" or not dr["rect"].intersects(LOGO) or dr["rect"].width > 100:
        continue
    rule = ' fill-rule="evenodd"' if dr.get("even_odd") else ""
    shapes.append(f'<path d="{path_of(dr["items"])}" fill="{hexof(dr["fill"])}"{rule}/>')

box = fitz.Rect(disc["scissor"])
for dr in page.get_drawings():
    if dr["type"] == "f" and dr["rect"].intersects(LOGO) and dr["rect"].width <= 100:
        box |= dr["rect"]
m = 0.5
vb = (box.x0 - m, box.y0 - m, box.width + 2 * m, box.height + 2 * m)
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(num(v) for v in vb)}" width="{num(vb[2] * 4)}" height="{num(vb[3] * 4)}">'
    "<title>Innovate BC</title>"
    + "".join(shapes) + "</svg>\n"
)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print(f"{OUT.relative_to(ROOT)}: {len(shapes)} shapes, {len(svg)} bytes, sha256 {hashlib.sha256(svg.encode()).hexdigest()}")
