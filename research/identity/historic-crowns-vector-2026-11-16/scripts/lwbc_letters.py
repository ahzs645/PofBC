import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit_letters
a = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); m = a.min(2) < 130
d = json.load(open(sys.argv[2])); U = '/usr/share/fonts/opentype/urw-base35/'
out = {}
for text in d:
    y0, y1, x0, x1 = d[text]['region']; r = m[y0:y1, x0:x1]
    res = {}
    for face in sys.argv[4].split(','):
        s0, p = d[text]['res'][face]; p.setdefault('hscale', 1.0)
        p2, dx, s, _, _ = fit_letters(text, U + face + '.otf', r, dict(p))
        res[face] = dict(iou=s, p=p2, dx=dx)
    print(text, {k: round(v['iou'], 4) for k, v in res.items()})
    out[text] = dict(region=d[text]['region'], res=res)
json.dump(out, open(sys.argv[3], 'w'), indent=0, default=float)
