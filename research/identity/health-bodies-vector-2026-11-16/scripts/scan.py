"""Quick survey of a PDF: per page, drawing count and fill colours; render first pages to PNG.
usage: python -I scan.py file.pdf outdir [maxpages]"""
import sys, collections
from pathlib import Path
import pymupdf as fitz
pdf, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 3
doc = fitz.open(pdf)
print(pdf.name, "pages", len(doc), doc.metadata.get("producer"), doc.metadata.get("creationDate"))
for i, page in enumerate(doc):
    if i >= maxp: break
    dr = page.get_drawings()
    cols = collections.Counter()
    for d in dr:
        if d.get("fill"): cols["#%02x%02x%02x" % tuple(round(v*255) for v in d["fill"][:3])] += 1
    imgs = page.get_images()
    print(f" p{i+1}: drawings={len(dr)} images={len(imgs)} fills={cols.most_common(8)}")
    page.get_pixmap(dpi=50).save(out / f"{pdf.stem}-p{i+1}.png")
