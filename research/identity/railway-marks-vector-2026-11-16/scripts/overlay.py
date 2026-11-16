"""Overlay check: render an SVG (in source-pixel coordinates via a transform) against the
binarised source crop. Writes a colour overlay (grey = both, red = source only,
blue = vector only) and prints IoU.

usage: overlay.py source.png vector.svg out.png [scale] [tx ty]  (SVG user units -> source px:
       px = tx + scale * u)
"""
import sys, subprocess, json, os, tempfile
import numpy as np
from PIL import Image

src, svg, out = sys.argv[1:4]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
tx = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
ty = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
thr = int(os.environ.get('THR', 128))
g = np.array(Image.open(src).convert('L'))
H, W = g.shape
s = open(svg).read()
import re
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
inner = s[s.index('>', s.index('<svg')) + 1: s.rindex('</svg>')]
wrap = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
        '<g transform="translate(%f %f) scale(%f) translate(%f %f)">%s</g></svg>' % (W * 4, H * 4, W, H, tx, ty, scale, -0.0, -0.0, inner))
# NB: svg content assumed to use its own coordinates starting at viewBox origin
tmp = tempfile.NamedTemporaryFile(suffix='.svg', delete=False); tmp.write(wrap.encode()); tmp.close()
png = tmp.name + '.png'
subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'render.js'), tmp.name, png, str(W * 4), 'white'], check=True)
r = np.array(Image.open(png).convert('L').resize((W, H), Image.BOX))
a = g < thr; b = r < thr
img = np.full((H, W, 3), 255, np.uint8)
img[a & ~b] = (230, 40, 40); img[b & ~a] = (40, 90, 230); img[a & b] = (70, 70, 70)
Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save(out)
print(json.dumps({'iou': round(float((a & b).sum() / (a | b).sum()), 4), 'sourceOnly': int((a & ~b).sum()), 'vectorOnly': int((b & ~a).sum())}))
