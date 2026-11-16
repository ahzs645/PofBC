"""BC Emergency Health Services, website layout — RECONSTRUCTION from original PDF parts.

  python -I bcehs_web_layout.py SOURCES_DIR

The website PNG has no endorsement line and sets the name smaller relative to the letters than the
endorsed lockup in the BCEHS Progress Report 2023-24 (page 1). No vector of the website layout was
found, so its three parts are taken from the report's own paths — the BCEHS letters, the red rule and
the two-line name — and each is scaled uniformly and placed on the box it occupies in the website PNG
(boxes measured from the PNG's alpha channel). Colours are the PDF's own.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import drawings_in, path_d, num, hexof

SRC = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "public/identity-expanded/bc-emergency-health-services"
p = fitz.open(SRC / "bcehs_progress_report_2023-24.pdf")[0]
ds = drawings_in(p, (420, 45, 605, 70), lambda d: d.get("fill") is not None)
letters = [d for d in ds if d["rect"].x1 < 516]
rule = [d for d in ds if 516 <= d["rect"].x0 < 522]
name = [d for d in ds if d["rect"].x0 >= 522]
assert len(letters) == 5 and len(rule) == 2 and len(name) == 25, (len(letters), len(rule), len(name))
def box(g):
    r = fitz.Rect(g[0]["rect"])
    for d in g: r |= d["rect"]
    return r
a = np.asarray(Image.open(OUT / "website-logo.png").convert("RGBA"))[..., 3] > 128
def ink(x0, x1):
    ys = np.where(a[:, x0:x1].any(1))[0]; xs = np.where(a[:, x0:x1].any(0))[0] + x0
    return fitz.Rect(xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
T_letters, T_rule, T_name = ink(0, 300), ink(300, 325), ink(325, a.shape[1])
out = []
def place(g, s, tx, ty):
    for d in g:
        out.append(f'<path d="{path_d(d["items"])}" fill="{hexof(d["fill"])}"' + (' fill-rule="evenodd"' if d.get("even_odd") else "")
                   + f' transform="matrix({num(s)} 0 0 {num(s)} {num(tx)} {num(ty)})"/>')
b = box(letters); s = T_letters.width / b.width; place(letters, s, T_letters.x0 - b.x0 * s, T_letters.y0 - b.y0 * s)
print("letters height fitted", b.height * s, "png", T_letters.height)
b = box(rule); s = T_rule.height / b.height; place(rule, s, (T_rule.x0 + T_rule.x1) / 2 - (b.x0 + b.x1) / 2 * s, T_rule.y0 - b.y0 * s)
b = box(name); s = T_name.width / b.width; place(name, s, T_name.x0 - b.x0 * s, T_name.y0 - b.y0 * s)
print("name height fitted", b.height * s, "png", T_name.height)
x0, y0 = T_letters.x0, min(T_letters.y0, T_rule.y0, T_name.y0); x1, y1 = T_name.x1, max(T_letters.y1, T_rule.y1, T_name.y1)
(OUT / "bcehs-website-layout-rebuilt.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x0)} {num(y0)} {num(x1 - x0)} {num(y1 - y0)}">'
    '<title>BC Emergency Health Services — logo (vector reconstruction)</title>'
    '<desc>Reconstruction: the BCEHS letters, rule and name are the BCEHS Progress Report 2023-24 cover paths, each scaled and placed to the website logo layout.</desc>'
    + "".join(out) + "</svg>\n")
