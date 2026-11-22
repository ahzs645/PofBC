"""Interior Health: symbol (original PDF vector) and stacked lockup (reconstruction from original PDF parts).

  python -I interior_health.py SOURCES_DIR

symbol: the three symbol paths of the stand-alone symbol at the top of 'Our Strategic Direction
2024-2027' (strategic-priorities.pdf, page 1), kept in the PDF's own colour.
stacked: no stacked original vector was found. The stacked layout is rebuilt from original parts:
the symbol paths and the 14 'Interior Health' glyph paths of the horizontal logo on the cover of
'Deciding to Move into Long-Term Care' (IH #810281, page 1), each scaled uniformly and positioned to
fit the official stacked JPG (bounding boxes measured from the JPG). Filled in IH Blue as specified
in IH's wayfinding guideline (RGB 47/79/136 = #2f4f88), which is also the colour of the stacked JPG.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import pymupdf as fitz
sys.path.insert(0, str(Path(__file__).parent))
from pdfvec import drawings_in, svg_of, path_d, num

SRC = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parents[4]
OUTDIR = ROOT / "public/identity-collected/interior-health"

# 1) symbol, original
sp = fitz.open(SRC / "strategic-priorities.pdf")[0]
sym = drawings_in(sp, (690, 20, 760, 66), lambda d: d.get("fill") is not None)
assert len(sym) == 3, len(sym)
(OUTDIR / "interior-health-symbol-2024-strategic-direction.svg").write_text(svg_of(
    sym, "Interior Health — symbol",
    "The three symbol paths from page 1 of Our Strategic Direction 2024-2027 (Interior Health, January 2024), PDF colours as converted by MuPDF."))

# 2) stacked, reconstruction
lp = fitz.open(SRC / "deciding-to-move-into-long-term-care.pdf")[0]
parts = drawings_in(lp, (380, 700, 580, 760), lambda d: d.get("fill") is not None)
symp = [d for d in parts if d["rect"].x1 < 460]
word = [d for d in parts if d["rect"].x0 > 460]
assert len(symp) == 3 and len(word) == 14
def bbox(ds):
    r = fitz.Rect(ds[0]["rect"])
    for d in ds: r |= d["rect"]
    return r
# measured on the stacked JPG (1080 x 592): ink boxes of the symbol and the wordmark
jpg = np.asarray(Image.open(ROOT / "public/identity-collected/interior-health/interior-health-stacked.jpg").convert("L")) < 128
rows = np.where(jpg.any(1))[0]
gap = [r for r in range(rows[0], rows[-1]) if not jpg[r].any()]
split = gap[len(gap) // 2]
def ink(a, y0):
    ys, xs = np.where(a); return fitz.Rect(xs.min(), ys.min() + y0, xs.max() + 1, ys.max() + 1 + y0)
js, jw = ink(jpg[:split], 0), ink(jpg[split:], split)
print("jpg symbol", js, "jpg wordmark", jw)
def place(ds, target, axis="w"):
    b = bbox(ds); s = target.width / b.width
    return [f'<path d="{path_d(d["items"])}" transform="matrix({num(s)} 0 0 {num(s)} {num(target.x0 - b.x0 * s)} {num(target.y0 - b.y0 * s)})"'
            + (' fill-rule="evenodd"' if d.get("even_odd") else "") + "/>" for d in ds], b.height * s
sp_, sh = place(symp, js)
wp_, wh = place(word, jw)
print("symbol height fitted vs jpg", sh, js.height, "wordmark height", wh, jw.height)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(min(js.x0, jw.x0))} {num(js.y0)} {num(max(js.x1, jw.x1) - min(js.x0, jw.x0))} {num(jw.y0 + wh - js.y0)}">'
       '<title>Interior Health — stacked (vector reconstruction)</title>'
       '<desc>Reconstruction: original symbol and wordmark paths from IH #810281 (2024), each scaled and positioned to fit the official stacked JPG; IH Blue #2f4f88.</desc>'
       '<g fill="#2f4f88">' + "".join(sp_ + wp_) + "</g></svg>\n")
(OUTDIR / "interior-health-stacked-rebuilt.svg").write_text(svg)
