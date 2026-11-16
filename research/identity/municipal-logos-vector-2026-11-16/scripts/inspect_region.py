"""List drawings, text spans and images inside a rectangle of a PDF page.
usage: inspect_region.py pdf page(1-based) x0 y0 x1 y1 [render.png]"""
import sys
import pymupdf
pdf, pno = sys.argv[1], int(sys.argv[2]) - 1
r = pymupdf.Rect(*map(float, sys.argv[3:7]))
page = pymupdf.open(pdf)[pno]
print('page rect', page.rect, 'rotation', page.rotation)
for i, d in enumerate(page.get_drawings()):
    if d['rect'].intersects(r):
        print(i, d['type'], [round(v, 1) for v in d['rect']], 'fill', d.get('fill') and tuple(round(c, 3) for c in d['fill']),
              'stroke', d.get('color') and tuple(round(c, 3) for c in d['color']), 'w', d.get('width'), 'op', d.get('fill_opacity'), len(d['items']))
for b in page.get_text('dict', clip=r)['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            print('TEXT', repr(s['text']), s['font'], round(s['size'], 1), [round(v) for v in s['bbox']])
for info in page.get_image_info(xrefs=True):
    if pymupdf.Rect(info['bbox']).intersects(r):
        print('IMAGE', info['xref'], [round(v) for v in info['bbox']], info['width'], info['height'])
if len(sys.argv) > 7:
    page.get_pixmap(dpi=200, clip=r).save(sys.argv[7])
