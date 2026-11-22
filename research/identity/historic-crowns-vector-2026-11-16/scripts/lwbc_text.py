"""Fit the LWBC lettering with candidate serif faces; report IoU per face."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit_text, init_text
a = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
m = a.min(2) < 130
U = '/usr/share/fonts/opentype/urw-base35/'
faces = {'NimbusRoman-Bold': U + 'NimbusRoman-Bold.otf', 'C059-Bold': U + 'C059-Bold.otf', 'P052-Bold': U + 'P052-Bold.otf', 'URWBookman-Demi': U + 'URWBookman-Demi.otf'}
lines = [('LWBC', (33, 93, 112, 345)), ('LAND AND WATER', (96, 117, 112, 345)), ('BRITISH COLUMBIA INC.', (117, 134, 112, 345))]
out = {}
for key, text_region in enumerate(lines):
    text, (y0, y1, x0, x1) = text_region
    r = m[y0:y1, x0:x1]
    ys, xs = np.where(r)
    cap = ys.max() - ys.min() + 1  # all caps lines
    if text.endswith('.'): pass
    res = {}
    for name, f in faces.items():
        best = None
        for hs in (1.0, 1.15, 1.3, 1.45):
            p0 = init_text(text, f, r, cap, ys.max() + 0.5, xs.min(), xs.max() + 1, hscale=hs)
            p0['hscale'] = hs
            b, s, _ = fit_text(text, f, r, p0, dict(x=0.5, y=0.5, size=0.5, tracking=5, hscale=0.04), rounds=4)
            if best is None or s > best[1]: best = (b, s)
        b, s = best
        res[name] = (round(s, 4), {k: float(v) for k, v in b.items()})
    best = max(res, key=lambda k: res[k][0])
    print(text, {k: v[0] for k, v in res.items()}, '->', best)
    out[text] = dict(res=res, region=[y0, y1, x0, x1])
json.dump(out, open(sys.argv[2], 'w'), indent=0)
