import sys, glob, collections, pymupdf as fitz
for f in sorted(glob.glob("*.pdf")):
    try: doc = fitz.open(f)
    except Exception: continue
    for i, p in enumerate(doc):
        if i > 30: break
        dr = p.get_drawings()
        fills = collections.Counter("#%02x%02x%02x" % tuple(round(v*255) for v in d["fill"][:3]) for d in dr if d.get("fill") and len(d["fill"])>=3)
        circ = [d for d in dr if d.get("fill") and "#%02x%02x%02x" % tuple(round(v*255) for v in d["fill"][:3]) in ("#517d98","#517c98","#4f7c97","#527e99")]
        white = fills.get("#ffffff", 0)
        if circ or white > 40:
            r = None
            for d in circ:
                r = fitz.Rect(d["rect"]) if r is None else r | d["rect"]
            print(f, f"p{i+1}", "circle", [tuple(round(x) for x in (r or (0,0,0,0)))], "white", white, "navy", fills.get("#091631",0), doc.metadata.get("creationDate","")[:10])
