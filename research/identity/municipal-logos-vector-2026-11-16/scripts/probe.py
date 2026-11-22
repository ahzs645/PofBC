"""Download a PDF (if URL) and summarise vector drawings / images per page.
usage: python3 -I probe.py <url-or-path> <outdir> [maxpages]"""
import sys, os, subprocess, hashlib
import pymupdf
src, outdir = sys.argv[1], sys.argv[2]
maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 4
os.makedirs(outdir, exist_ok=True)
if src.startswith('http'):
    name = hashlib.sha1(src.encode()).hexdigest()[:10] + '.pdf'
    path = os.path.join(outdir, name)
    if not os.path.exists(path):
        r = subprocess.run(['curl', '-sSL', '--max-time', '180', '-A', 'Mozilla/5.0', '-o', path, '-w', '%{http_code} %{content_type}', src], capture_output=True, text=True)
        print('download', r.stdout, r.stderr.strip())
else:
    path = src
doc = pymupdf.open(path)
print(path, 'pages', doc.page_count, doc.metadata.get('creator'), '|', doc.metadata.get('producer'), '|', doc.metadata.get('creationDate'))
for i in range(min(maxp, doc.page_count)):
    pg = doc[i]
    dr = pg.get_drawings(); im = pg.get_images()
    cols = {}
    for d in dr:
        c = d.get('fill') or d.get('color')
        if c: cols[tuple(round(x, 3) for x in c)] = cols.get(tuple(round(x, 3) for x in c), 0) + 1
    top = sorted(cols.items(), key=lambda kv: -kv[1])[:6]
    print(f' p{i+1} drawings={len(dr)} images={len(im)} topcols={top}')
    os.makedirs(os.path.join(outdir, 'thumbs'), exist_ok=True)
    pg.get_pixmap(dpi=40).save(os.path.join(outdir, 'thumbs', f'{os.path.basename(path)}-p{i+1}.png'))
