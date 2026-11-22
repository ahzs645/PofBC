"""Contact sheet of first N pages of PDFs, plus a summary of vector/image counts.  usage: firstpages.py out.png N files..."""
import sys, collections, pymupdf as fitz
from PIL import Image
out, n, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = []
for f in files:
    try: d = fitz.open(f)
    except Exception as e: print(f, e); continue
    for i in range(min(n, len(d))):
        p = d[i]
        c = collections.Counter("#%02x%02x%02x" % tuple(round(v*255) for v in x["fill"][:3]) for x in p.get_drawings() if x.get("fill") and len(x["fill"]) >= 3)
        print(f, f"p{i+1}", d.metadata.get("creator"), (d.metadata.get("creationDate") or "")[:10], "draw", sum(c.values()), c.most_common(5), "img", len(p.get_images()))
        pix = p.get_pixmap(dpi=22); ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples) if pix.n == 3 else Image.frombytes("RGBA", (pix.width, pix.height), pix.samples).convert("RGB"))
W = sum(i.width for i in ims) + 6 * len(ims); H = max(i.height for i in ims)
s = Image.new("RGB", (W, H), "gray"); x = 0
for i in ims: s.paste(i, (x, 0)); x += i.width + 6
s.save(out)
