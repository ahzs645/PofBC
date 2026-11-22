"""Generic: fit lines of type with candidate faces (line fit, then per-letter spacing).
fit_lines.py SRC THR OUT.json FACES 'text|y0|y1|x0|x1|baseline|captop' ..."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit_text, init_text, fit_letters
U = '/usr/share/fonts/opentype/urw-base35/'
src, thr, out, faces = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4].split(',')
a = np.array(Image.open(src).convert('RGB')).astype(int); m = a.min(2) < thr
from scipy import ndimage
lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1))
m = np.isin(lab, [i + 1 for i, sz in enumerate(sizes) if sz >= 8])  # drop scan speckle
res = {}
for spec in sys.argv[5:]:
    text, y0, y1, x0, x1, base, captop = spec.split('|'); y0, y1, x0, x1 = map(int, (y0, y1, x0, x1)); base = float(base) - y0; captop = float(captop) - y0
    r = m[y0:y1, x0:x1]; ys, xs = np.where(r)
    R = {}
    for face in faces:
        f = face if face.startswith('/') else U + face + '.otf'
        p0 = init_text(text, f, r, base - captop, base, xs.min(), xs.max() + 1)
        p0['hscale'] = 1.0
        b, s, _ = fit_text(text, f, r, p0, dict(x=0.5, y=0.5, size=0.5, tracking=5), rounds=3)
        p2, dx, s2, _, _ = fit_letters(text, f, r, dict(b), rounds=3)
        R[face] = dict(iou=s2, p=p2, dx=dx)
    print(text, {k: round(v['iou'], 4) for k, v in R.items()})
    res[text] = dict(region=[y0, y1, x0, x1], res=R)
json.dump(res, open(out, 'w'), indent=0, default=float)
