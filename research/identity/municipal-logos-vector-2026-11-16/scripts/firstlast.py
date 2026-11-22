"""Download PDFs; print metadata; render first and last pages to <outdir>/thumbs for a look.
usage: firstlast.py outdir url [url ...]"""
import sys, os, subprocess, hashlib
import pymupdf
outdir = sys.argv[1]; os.makedirs(os.path.join(outdir, 'thumbs'), exist_ok=True)
for u in sys.argv[2:]:
    path = os.path.join(outdir, hashlib.sha1(u.encode()).hexdigest()[:10] + '.pdf')
    if not os.path.exists(path):
        subprocess.run(['curl', '-sSL', '--max-time', '200', '-A', 'Mozilla/5.0', '-o', path, u])
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        print('FAIL', u, e); continue
    print(os.path.basename(path), doc.page_count, (doc.metadata.get('creator') or '')[:30], (doc.metadata.get('creationDate') or '')[:10], u)
    for i in sorted({0, doc.page_count - 1}):
        pg = doc[i]
        print('   p', i + 1, 'drawings', len(pg.get_drawings()), 'images', len(pg.get_images()))
        pg.get_pixmap(dpi=40).save(os.path.join(outdir, 'thumbs', f'{os.path.basename(path)[:-4]}-p{i+1}.png'))
