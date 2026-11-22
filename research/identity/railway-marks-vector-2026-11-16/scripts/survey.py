import sys, os, warnings
warnings.filterwarnings('ignore')
import pymupdf as fitz
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for fn in sorted(os.listdir(src)):
    p = os.path.join(src, fn)
    try:
        d = fitz.open(p)
    except Exception as e:
        print(fn, 'ERR', e); continue
    if d.page_count == 0: print(fn, 'empty'); continue
    pg = d[0]
    dr = pg.get_drawings(); im = pg.get_images(full=True)
    fonts = [f[3] for f in pg.get_fonts()]
    meta = d.metadata
    print(f"{fn}: pages={d.page_count} drawings={len(dr)} images={[(i[2],i[3]) for i in im]} fonts={fonts[:6]} creator={meta.get('creator')}|{meta.get('producer')} date={meta.get('creationDate')}")
    pix = pg.get_pixmap(dpi=40)
    pix.save(os.path.join(out, fn.replace('.pdf','.png')))
