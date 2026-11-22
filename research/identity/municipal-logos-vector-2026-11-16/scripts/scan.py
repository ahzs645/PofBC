"""Find pages whose vector fills use given colours. usage: scan.py pdf '#rrggbb,#rrggbb' [tol]"""
import sys
import pymupdf
doc = pymupdf.open(sys.argv[1])
want = [tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) for h in sys.argv[2].split(',')]
tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
for pg in doc:
    hits = [0] * len(want)
    for d in pg.get_drawings():
        c = d.get('fill') or d.get('color')
        if not c or len(c) != 3: continue
        for k, w in enumerate(want):
            if max(abs(a - b) for a, b in zip(c, w)) <= tol: hits[k] += 1
    if all(hits):
        print('page', pg.number + 1, hits)
