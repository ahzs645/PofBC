"""List pages whose vector fills include blues near IH blue (any CMYK->RGB conversion), with counts and bboxes.
usage: python -I findblue.py files..."""
import sys, pymupdf as fitz
def bluish(c):
    r,g,b = c[:3]
    return b > 0.45 and b > r + 0.25 and g < 0.6
for f in sys.argv[1:]:
    try: doc = fitz.open(f)
    except Exception as e: print(f, "ERR", e); continue
    for i, p in enumerate(doc):
        if i >= 40: break
        ds = [d for d in p.get_drawings() if d.get("fill") and len(d["fill"]) >= 3 and bluish(d["fill"]) and len(d["items"]) >= 3]
        if ds:
            r = fitz.Rect(ds[0]["rect"])
            for d in ds: r |= d["rect"]
            cols = sorted({"#%02x%02x%02x" % tuple(round(v*255) for v in d["fill"][:3]) for d in ds})
            print(f"{f} p{i+1} n={len(ds)} bbox={tuple(round(x) for x in r)} cols={cols[:4]}")
