"""First Nations Health Authority.

  python -I fnha.py SOURCES_DIR

1. fnha-white-stacked-2026-pdf.svg — ORIGINAL: the all-white centred stacked logo (symbol over the
   two centred lines) from the front panel of the 'Indigenous End-of-Life Guide' brochure (FNHA,
   PDF created 16 September 2026, page 1), as the PDF's own white paths. (The white logo on 'A Guide
   to Your Baby's First Foods' is a different arrangement — tagline flush right — so it was not used.) Two zero-width hairline strokes (detail at the eye) are written at 0.35 pt,
   the width the same two strokes have in the Caregiving PDF.
2. fnha-horizontal-colour-rebuilt.svg — RECONSTRUCTION from original parts: no full-colour horizontal
   vector was found. Lettering = the white horizontal logo's own glyph paths ('Caregiving: An Important
   Part of Community Medicine', page 1), filled with the navy #091631 the colour logos use; symbol = the
   full-colour symbol paths of the stacked logo in 'Connect to Change, Movement is Medicine' (Daily
   Movement Guide, May 2026, page 1), scaled uniformly onto the white horizontal symbol's box.
"""
import sys
from pathlib import Path
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import drawings_in, svg_of, path_d, num, hexof

SRC = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "public/identity-collected/first-nations-health-authority"
white = lambda d: (d.get("fill") and hexof(d["fill"]) == "#ffffff") or (d["type"] == "s" and d.get("color") and hexof(d["color"]) == "#ffffff")

def fix_hairlines(ds, w=0.35):
    for d in ds:
        if d["type"] == "s" and not d.get("width"):
            d["width"] = w
    return ds

# 1 white stacked
p = fitz.open(SRC / "FNHA-Indigenous-End-of-Life-Guide-Brochure.pdf")[0]
ws = fix_hairlines(drawings_in(p, (570, 15, 750, 110), white))
print("white stacked paths", len(ws))
(OUT / "fnha-white-stacked-2026-pdf.svg").write_text(svg_of(ws, "First Nations Health Authority — white, stacked",
    "Original vector paths from page 1 of the Indigenous End-of-Life Guide brochure (First Nations Health Authority, 2026); white artwork for a dark ground."))

# 2 colour horizontal, reconstruction
cg = fitz.open(SRC / "FNHA-Caregiving-An-Important-Part-of-Community-Medicine-3.pdf")[0]
hz = fix_hairlines(drawings_in(cg, (100, 880, 520, 1000), white))
sym_w = [d for d in hz if d["rect"].x1 < 255]
txt = [d for d in hz if d["rect"].x0 >= 255]
def box(ds):
    r = fitz.Rect(ds[0]["rect"])
    for d in ds: r |= d["rect"]
    return r
dm = fitz.open(SRC / "FNHA-Daily-Movement-Guide.pdf")[0]
sym_c = [d for d in drawings_in(dm, (650, 500, 760, 545)) if d.get("fill") is not None or d["type"] == "s"]
sym_c = fix_hairlines(sym_c)
bw, bc = box(sym_w), box(sym_c)
print("white symbol box", bw, "aspect", bw.width / bw.height, "colour symbol box", bc, "aspect", bc.width / bc.height, len(sym_c), "paths;", len(txt), "glyphs")
s = bw.width / bc.width
tx, ty = bw.x0 - bc.x0 * s, bw.y1 - bc.y1 * s   # align widths and baselines of the two symbols
parts = []
for d in sym_c:
    a = []
    if d.get("fill") is not None:
        a.append(f'fill="{hexof(d["fill"])}"' + (' fill-rule="evenodd"' if d.get("even_odd") else ""))
    else:
        a.append('fill="none"')
    if d["type"] in ("s", "fs") and d.get("color") is not None:
        a.append(f'stroke="{hexof(d["color"])}" stroke-width="{num(d["width"])}"')
    parts.append(f'<path d="{path_d(d["items"])}" {" ".join(a)}/>')
g_sym = f'<g transform="matrix({num(s)} 0 0 {num(s)} {num(tx)} {num(ty)})">' + "".join(parts) + "</g>"
g_txt = '<g fill="#091631">' + "".join(f'<path d="{path_d(d["items"])}"' + (' fill-rule="evenodd"' if d.get("even_odd") else "") + "/>" for d in txt if d.get("fill") is not None) + "</g>"
full = box(hz)
top = min(full.y0, ty + bc.y0 * s)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(full.x0)} {num(top)} {num(full.width)} {num(full.y1 - top)}">'
       '<title>First Nations Health Authority — full colour, horizontal (vector reconstruction)</title>'
       '<desc>Reconstruction from original FNHA PDF parts: full-colour symbol paths (Daily Movement Guide, 2026) placed on the white horizontal logo (Caregiving handout), whose glyph paths are filled navy #091631.</desc>'
       + g_sym + g_txt + "</svg>\n")
(OUT / "fnha-horizontal-colour-rebuilt.svg").write_text(svg)
