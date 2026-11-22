"""BC Women's Hospital + Health Centre logo, from page 4 of the BC Women's Health Foundation
Impact Report 2024 (single pages; InDesign 19.0, created 13 August 2024), top left.

  python -I bc_womens.py SOURCES_DIR [pairing a|b] [page-render.png]

Two folds are drawn twice (two images under two clips with the same box); pairing "a" (image
order = clip order) matched a MuPDF render of the page better than "b" (mean abs. difference over
the W 8.1 vs 8.6 levels), so "a" is the default.

The PDF draws the logo as:
  * the lettering: 46 filled glyph paths (teal and grey), kept as they are;
  * the W ribbon: each of its bands and small joins is a clipping path (kept as is) filled with
    hundreds of thin horizontal rectangles, a gradient expanded into strips by the publishing
    software; and three folds, each a clipping path (kept) filled with a 34 x 43 px CMYK image whose
    rows are uniform (each image is a vertical colour ramp).
In the SVG each clipping path is filled with an SVG linear gradient running top to bottom whose
stops are the strips' own colours at the strips' own heights (MuPDF's CMYK->sRGB conversion), and
each fold's image is replaced by a linear gradient through the image's row colours (MuPDF's
CMYK->sRGB conversion, every row kept as a stop). Geometry is the PDF's own; no tracing.
A hidden PHSA line sits under the logo in the PDF (it does not render); it is not included.
"""
import sys
from pathlib import Path
import numpy as np
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import path_d, num, hexof

SRC = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parents[4]
PAIR = sys.argv[2] if len(sys.argv) > 2 else "a"
OUT = ROOT / "public/identity-expanded/sub-bc-womens-hospital/bc-womens-2024-foundation-impact-report.svg"
doc = fitz.open(SRC / "bcwhf-BCWHF-Impact-Report-2024-Single-Pages.pdf"); page = doc[3]
LOGO = fitz.Rect(30, 130, 170, 166.4)
WBOX = fitz.Rect(116, 133, 165, 165)
ext = page.get_drawings(extended=True)

# lettering and W pieces in drawing order
items, cur = [], None
for i, e in enumerate(ext):
    if e["type"] == "clip":
        cur = i; continue
    if e["type"] == "group" or not LOGO.contains(e["rect"]):
        continue
    items.append((i, cur, e))
glyphs = [e for i, c, e in items if not WBOX.intersects(e["rect"]) or e["rect"].x1 < 116]
strips = {}
for i, c, e in items:
    if e["rect"].x0 >= 116:
        strips.setdefault(c, []).append(e)

# image folds: clip index -> image xref (pairing for the two doubled folds chosen by render check)
IMG = {1530: 55, 1531: 56 if PAIR == "a" else 57, 1532: 57 if PAIR == "a" else 56, 1655: 58 if PAIR == "a" else 59, 1674: 59 if PAIR == "a" else 58}
bbox_of = {info["xref"]: fitz.Rect(info["bbox"]) for info in page.get_image_info(xrefs=True) if info["xref"] in IMG.values() and WBOX.contains(fitz.Rect(info["bbox"]))}

defs, body = [], []
def gradient(gid, y0, y1, stops):
    # drop interior stops identical to both neighbours
    keep = [s for k, s in enumerate(stops) if k in (0, len(stops) - 1) or not (stops[k - 1][1] == s[1] == stops[k + 1][1])]
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{num(y0)}" x2="0" y2="{num(y1)}">'
            + "".join(f'<stop offset="{max(0, min(1, (y - y0) / (y1 - y0))):.4f}" stop-color="{c}"/>' for y, c in keep) + "</linearGradient>")

order = sorted(set(strips) | set(IMG))
for c in order:
    clip = ext[c]; sc = fitz.Rect(clip["scissor"])
    cid, gid = f"w{c}", f"g{c}"
    defs.append(f'<clipPath id="{cid}"><path d="{path_d(clip["items"])}"' + (' clip-rule="evenodd"' if clip.get("even_odd") else "") + "/></clipPath>")
    if c in strips:
        ss = sorted(strips[c], key=lambda e: e["rect"].y0)
        assert all(abs(e["rect"].x0 - ss[0]["rect"].x0) < 0.6 for e in ss), c
        y0, y1 = min(e["rect"].y0 for e in ss), max(e["rect"].y1 for e in ss)
        stops = [((e["rect"].y0 + e["rect"].y1) / 2, hexof(e["fill"])) for e in ss]
        x0, x1 = min(e["rect"].x0 for e in ss), max(e["rect"].x1 for e in ss)
    else:
        xref = IMG[c]; pm = fitz.Pixmap(doc, xref)
        if pm.colorspace is None or pm.colorspace.n != 3:
            pm = fitz.Pixmap(fitz.csRGB, pm)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n)[..., :3]
        b = bbox_of[xref]; y0, y1, x0, x1 = b.y0, b.y1, b.x0, b.x1
        h = pm.height
        stops = [(y0 + (r + 0.5) * (y1 - y0) / h, "#%02x%02x%02x" % tuple(int(round(v)) for v in a[r].mean(0))) for r in range(h)]
    defs.append(gradient(gid, y0, y1, stops))
    body.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}" height="{num(y1 - y0)}" fill="url(#{gid})" clip-path="url(#{cid})"/>')

letters = "".join(f'<path d="{path_d(e["items"])}" fill="{hexof(e["fill"])}"' + (' fill-rule="evenodd"' if e.get("even_odd") else "") + "/>" for e in glyphs)
u = fitz.Rect(glyphs[0]["rect"])
for e in glyphs: u |= e["rect"]
for c in order: u |= (fitz.Rect(ext[c]["scissor"]) & WBOX)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(u.x0)} {num(u.y0)} {num(u.width)} {num(u.height)}">'
       "<title>BC Women's Hospital + Health Centre — logo</title>"
       "<desc>From page 4 of the BC Women's Health Foundation Impact Report 2024: the PDF's own glyph and clipping paths; the W's strip-expanded gradients and three fold images rewritten as SVG linear gradients through their own colours.</desc>"
       "<defs>" + "".join(defs) + "</defs>" + letters + "".join(body) + "</svg>\n")
OUT.write_text(svg)
print(len(glyphs), "glyphs;", len(order), "W pieces;", u)
if len(sys.argv) > 3:  # optional: the page itself rendered over the same box, for comparison
    page.get_pixmap(dpi=400, clip=u).save(sys.argv[3])
