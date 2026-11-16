import sys, json; sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import raster_eo
from textpath import layout, polys
U = '/usr/share/fonts/opentype/urw-base35/'
d = json.load(open(sys.argv[2])); a = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); m = a.min(2) < int(sys.argv[5]) if len(sys.argv) > 5 else a.min(2) < 130
rows = []
for text in d:
    y0, y1, x0, x1 = d[text]['region']; r = m[y0:y1, x0:x1]
    for face in sys.argv[4].split(','):
        R = d[text]['res'][face]; p = R['p']; dx = R['dx']; f = face if face.startswith('/') else U + face + '.otf'
        pl, _ = layout(text, f, p['size'], p['x'], p['y'], p.get('tracking', 0), p.get('hscale', 1), p.get('slant', 0))
        pl = [(g, (A, B, C, D, E + dx[i], F)) for i, (g, (A, B, C, D, E, F)) in enumerate(pl)]
        t = raster_eo(polys(pl, f), (x1 - x0, y1 - y0))
        im = np.full(r.shape + (3,), 255, np.uint8); im[r & t] = (60, 60, 60); im[r & ~t] = (40, 120, 235); im[~r & t] = (230, 40, 160)
        rows.append(Image.fromarray(im).resize(((x1 - x0)*3, (y1 - y0)*3), Image.NEAREST))
W = max(i.width for i in rows); H = sum(i.height + 4 for i in rows)
s = Image.new('RGB', (W, H), 'white'); y = 0
for i in rows: s.paste(i, (0, y)); y += i.height + 4
s.save(sys.argv[3])
