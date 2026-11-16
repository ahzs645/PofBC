"""Download PDFs and report pages where small vector fills use every given colour.
usage: hunt.py <outdir> '<#hex,#hex>' <tol> url [url ...]   (prints url -> local file, hits)"""
import sys, os, subprocess, hashlib
import pymupdf
outdir, cols, tol, urls = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4:]
want = [tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) for h in cols.split(',')]
os.makedirs(outdir, exist_ok=True)
for u in urls:
    path = os.path.join(outdir, hashlib.sha1(u.encode()).hexdigest()[:10] + '.pdf')
    if not os.path.exists(path):
        subprocess.run(['curl', '-sSL', '--max-time', '200', '-A', 'Mozilla/5.0', '-o', path, u])
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        print('FAIL', u, e); continue
    found = []
    for pg in doc:
        hits = [0] * len(want)
        for d in pg.get_drawings():
            c = d.get('fill') or d.get('color')
            if not c or len(c) != 3 or d['rect'].width > 300: continue
            for k, w in enumerate(want):
                if max(abs(a - b) for a, b in zip(c, w)) <= tol: hits[k] += 1
        if all(hits): found.append((pg.number + 1, hits))
    print(os.path.basename(path), doc.page_count, (doc.metadata.get('creator') or '')[:30], u, found[:8])
